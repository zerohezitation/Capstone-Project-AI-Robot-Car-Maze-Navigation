import argparse
import socket
from threading import Thread
import cv2
import struct
import base64

from common.camera import Camera
from common.utils import get_ip

"""
Streamer
A video streaming server. 
This is run on the raspberry pi robot, and it will listen for remote connections.
Once connected, the server will encode the camera frames and send them to the client
to decode and display. See streamer_client.py for the client application.

This gets run in the background when you start the middleware, but you can also run this
file independently to run the streamer standalone without the middleware:

python3 -m middleware.streamer
"""


class Streamer():
    def __init__(self, camera: Camera, interface: str = "wlan0", port: int = 8125) -> None:
        self.camera = camera

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = get_ip(interface)

        s.bind((host, port))
        s.listen(10)
        print(f"Video stream is being served at {host}:{port}")

        self.should_stop = False
        self.t = Thread(target=self.worker, args=[s])
        self.t.start()

    # Worker thread, continuously reads the camera buffer and sends the frames to the client
    def worker(self, s: socket.socket):
        try:
            while not self.should_stop:
                # s.settimeout(0)
                # Accept a remote connection
                print(f"Video stream waiting for connection...")
                conn, addr = s.accept()
                print(f"Video stream connected to {addr}")

                # Start sending frames to the client once connected
                while not self.should_stop:
                    photo = self.camera.read()  # read a camera frame

                    # Enocode to base64
                    retval, buffer = cv2.imencode('.jpg', photo)
                    jpg_as_text = base64.b64encode(buffer)

                    # Get the size of the image and encode to byte for header
                    message_size = struct.pack("Q", len(jpg_as_text))

                    try:
                        # Message format: Size of enocded image, followed by that number of bytes
                        conn.sendall(message_size + jpg_as_text)
                    except:
                        # If there was an error, close the connection and accept a new connection
                        break

                print(f"Closing video stream connection with {addr}")
                conn.close()
        finally:
            print("Closing video stream socket")
            s.close()

    # Signal the worker thread to stop
    def stop(self):
        self.should_stop = True
        self.t.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python3 -m middleware.streamer",
        description="Video Streaming Server for Raspberry Pi Robot. Use to send the video stream to a remote client.",
    )
    parser.add_argument(
        "-i", "--interface", help="the name of the network interface to host the connection on (usually 'wlan0' for the Raspberry Pi wireless interface)", default="wlan0", dest="interface")
    parser.add_argument(
        "-p", "--port", help="the port to host the connection on (usually 8125)", default=8125, type=int)
    args = parser.parse_args()

    camera = Camera()
    with camera as cam:
        Streamer(cam, args.interface, args.port)

        while True:
            pass
