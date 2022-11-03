import argparse
import socket
from threading import Thread
import cv2
import struct
import base64
import logging

from common.camera import Camera
from common.physical_camera import PhysicalCamera
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

        self.sentinel = False
        self.t = Thread(target=self.worker, args=[interface, port])
        self.t.start()

    # Entering the context of a camera "with Camera() as cam"
    def __enter__(self):
        return self

    # When exiting the context of the camera, stop the worker threads
    def __exit__(self, type, value, traceback):
        self.sentinel = True
        if self.t is not None:
            logging.debug(
                f"Waiting for video streamer worker thread to finish...")
            self.t.join()
        logging.debug(f"Streamer is exiting.")

    # Worker thread, continuously reads the camera buffer and sends the frames to the client
    def worker(self, interface: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host = get_ip(interface)

            s.bind((host, port))
            s.listen(10)

            # Make the socket non-blocking so that we don't get stuck on s.accept()
            # Otherwise we won't be able to call .join() on the worker thread when trying to terminate the program
            s.settimeout(1)

            logging.info(f"Video stream is being served at {host}:{port}")
            while not self.sentinel:
                try:
                    conn, addr = s.accept()
                    with conn:
                        logging.info(f"Video stream connected to {addr}")

                        # Start sending frames to the client once connected
                        while not self.sentinel:
                            frame = self.camera.read()

                            # Enocode to base64
                            retval, buffer = cv2.imencode('.jpg', frame)
                            jpg_as_text = base64.b64encode(buffer)

                            # Get the size of the image and encode to byte for header
                            message_size = struct.pack("Q", len(jpg_as_text))

                            # Message format: Size of enocded image, followed by that number of bytes
                            conn.sendall(message_size + jpg_as_text)

                except socket.timeout:
                    # If we're here, a connection wasn't made within the timeout window
                    # Immediately continue checking for connections
                    continue
                except BrokenPipeError:
                    # If we're here, the client terminated the connection and we were unable to send the frame
                    # Close the connection and try to connect to a new host
                    break
                except BlockingIOError as e:
                    logging.error("Error with video streaming server.", e)
                    break


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

    with PhysicalCamera() as cam:
        streamer = None
        try:
            streamer = Streamer(cam, args.interface, args.port)
            while True:
                pass
        except KeyboardInterrupt:
            pass
        finally:
            if streamer is not None:
                streamer.stop()
