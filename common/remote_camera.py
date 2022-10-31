import argparse
import pickle
import socket
import struct
from threading import Thread, Lock, Event
import numpy as np
import base64
import cv2
import time
import os
from datetime import datetime

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
        self.buffer = None
        self.lock = Lock()

        self.ev = Event()

        self.t = Thread(target=self.worker, args=[host, port])
        self.t.start()

    def worker(self, host: str, port: int):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(f"Connecting to {host}:{port}")
        s.connect((host, port))
        print('Connected')

        while True:
            data = b''
            payload_size = 8  # struct.calcsize("L")

            while True:

                # Retrieve message size (the first 8 bytes)
                try:
                    while len(data) < payload_size:
                        data += s.recv(4096)
                except TimeoutError:
                    continue

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                # Convert hex -> int size of payload
                msg_size = struct.unpack("L", packed_msg_size)[0]
                # Retrieve all data based on message size
                while len(data) < msg_size:
                    data += s.recv(4096)

                # Get the frame from the application buffer based on message size
                frame_data = data[:msg_size]
                # Don't throw away any extra data, it might contain the next frame
                data = data[msg_size:]

                #img = self.decode_frame(frame_data)
                nparr = np.frombuffer(base64.b64decode(frame_data), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                self.lock.acquire()
                self.buffer = np.copy(img)
                self.lock.release()
                self.ev.set()

    def decode_frame(self, frame):
        nparr = np.frombuffer(base64.b64decode(frame), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def read(self):
        frame = None
        while frame is None or len(np.shape(frame)) == 0:
            self.lock.acquire()
            frame = np.copy(self.buffer)
            self.lock.release()
            if frame is None or len(np.shape(frame)) == 0:
                time.sleep(0.5)
        return frame


def save_images(stream: RemoteCamera):
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
    from middleware.devices.sensors.ai_sensor import AiSensor
    ai = AiSensor(stream)
    while True:
        print(ai.run())
        time.sleep(0.1)


def view(stream: RemoteCamera):
    while True:
        frame = stream.read()
        cv2.imshow("Stream", frame)
        cv2.waitKey(1)
        # time.sleep(1)


def view_processed(stream: RemoteCamera, both=False):
    with ProcessedCamera(stream) as cam_proc:
        while True:
            frame = cam_proc.read()
            print(np.shape(frame))
            if frame:
                cv2.imshow("Processed Stream", frame)
                cv2.waitKey(1)
            # time.sleep(1)


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

    stream = RemoteCamera(args.host, args.port)
    if args.mode == "capture":
        save_images(stream)
    elif args.mode == "ai":
        test_ai(stream)
    elif args.mode == "view":
        view(stream)
    elif args.mode == "view_p":
        view_processed(stream)
