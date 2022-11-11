import argparse
import pickle
import socket
import struct
from threading import Thread
import numpy as np
import base64
import cv2
import time
import os
from datetime import datetime
import logging

from common.camera import Camera
from common.processed_camera import ProcessedCamera

"""
RemoteCamera
A video streaming client that can connect to the camera of the robot raspberry pi car.

First, run the streamer server on the robot itself (This automatically starts
with the middleware, or you can run it separately. See streamer.py.)

Once the server is running, on a remote machine connected to the raspberry pi,
you can run the client:

python3 -m common.remote_camera <ip of robot> -m <mode>

Mode "view": View the raw camera feed
Mode "view_p": View the processed camera feed (processing done on the client side)
Mode "capture": Enter capture mode. Used to capture frames for training data.
Mode "ai": Run the AiSensor on the client using the streamed video.
"""


class RemoteCamera(Camera):
    def __init__(self, host: str, port: int = 8125) -> None:
        super().__init__()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s.setblocking(False)

        self.t = Thread(target=self.worker, args=[host, port])
        self.t.start()

    # TODO fix this so that the socket closes when the server shuts down
    # Currently it hangs on self.s.connect() becuase it's waiting for IO
    # Like the other sockets in the project, we should setblocking(False)
    # and handle the timeout exception so that we can close the thread from the parent
    def __exit__(self, type, value, traceback):
        self.s.shutdown(socket.SHUT_WR)
        self.s.close()
        return super().__exit__(type, value, traceback)

    def worker(self, host: str, port: int):
        # Connect to the robot hosting the video streaming server
        print(f"Connecting to {host}:{port}...")
        self.s.connect((host, port))
        print(f"Connected to {host}:{port}")

        while not self.stop:
            data = b''
            payload_size = 8  # struct.calcsize("L")

            while True:
                try:
                    while len(data) < payload_size:
                        # Retrieve message size (the first 8 bytes)
                        data += self.s.recv(4096)

                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    # Convert hex -> int size of payload
                    msg_size = struct.unpack("L", packed_msg_size)[0]
                    # Retrieve all data based on message size
                    while len(data) < msg_size:
                        data += self.s.recv(4096)

                    # Get the frame from the application buffer based on message size
                    frame_data = data[:msg_size]
                    # Don't throw away any extra data, it might contain the next frame
                    data = data[msg_size:]

                    img = self.decode_frame(frame_data)
                    #nparr = np.frombuffer(base64.b64decode(frame_data), np.uint8)
                    #img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    super().write(img)
                except OSError:
                    logging.warning(
                        f"Ending connection with {host}:{port}")
                    self.stop = True
                    break

    # Decode the base64 frame to a CV2 color image
    def decode_frame(self, frame):
        nparr = np.frombuffer(base64.b64decode(frame), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img


def save_images(stream: RemoteCamera):
    # Enter the mode for taking training data from a remote camera
    labels = ["OffsetLeft", "Straight", "OffsetRight"]
    timestamp = time.time()
    date_time = datetime.fromtimestamp(timestamp)
    str_time = date_time.strftime(r"%I_%M_%S_%f")
    root_path = f"dataset_{str_time}"
    os.mkdir(root_path)

    with ProcessedCamera(stream) as cam_proc:
        for label in labels:
            idx = 1
            print("-------------------------------------------------------")
            print(f"Class: {label}")
            class_path = os.path.join(root_path, label)
            os.mkdir(class_path)

            while True:
                command = input(
                    "Take image? (Type 'next' to move to the next class)")
                if command == "next":
                    break
                image = cam_proc.read()

                timestamp = time.time()
                date_time = datetime.fromtimestamp(timestamp)
                str_time = date_time.strftime(r"%I_%M_%S_%f")
                new_path = os.path.join(class_path, f"{str_time}.png")
                cv2.imwrite(new_path, image)
                print(f"\tImage #{idx}: {str_time}.png")
                idx += 1


def test_ai(stream: RemoteCamera):
    # Test the AI model using the remote video camera
    from middleware.devices.sensors.track_offset_sensor import TrackOffsetSensor
    with ProcessedCamera(stream) as cam_proc:
        ai = TrackOffsetSensor(cam_proc)
        times = []
        while True:
            s = time.time()
            cv2.imshow("Stream", cam_proc.read())
            print(ai.run())
            e = time.time()
            times = [e-s] + times[:100]
            print((np.average(times) ** -1) / 100)
            cv2.waitKey(1)
            time.sleep(0.1)


def view(stream: RemoteCamera):
    # View the raw video stream (color, not processed)
    while True:
        frame = stream.read()
        cv2.imshow("Stream", frame)
        cv2.waitKey(1)


def view_processed(stream: RemoteCamera, both=False):
    # View the processed video stream (resize, grayscale, canny, etc)
    with ProcessedCamera(stream) as cam_proc:
        while True:
            frame = cam_proc.read()
            print(np.shape(frame))
            if frame:
                cv2.imshow("Processed Stream", frame)
                cv2.waitKey(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python3 -m common.remote_camera",
        description="Video Streaming Client for Raspberry Pi Robot. Use to remotely connect to the robot's camera.",
    )
    parser.add_argument(
        "host", help="the robot ip address")
    parser.add_argument("-p", "--port", type=int,
                        help="the robot video streaming server port (usually 8125)", default=8125, dest="port")
    parser.add_argument("-m", "--mode", help="Choose program mode. ",
                        choices=["capture", "ai", "view", "view_p", "view_both"], default="view", dest="mode")
    args = parser.parse_args()

    try:
        with RemoteCamera(args.host, args.port) as stream:
            if args.mode == "capture":
                save_images(stream)
            elif args.mode == "ai":
                test_ai(stream)
            elif args.mode == "view":
                view(stream)
            elif args.mode == "view_p":
                view_processed(stream)
    except KeyboardInterrupt:
        pass
