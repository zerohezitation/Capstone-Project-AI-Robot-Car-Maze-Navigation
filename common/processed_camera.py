from threading import Lock, Thread
import time

import numpy as np

from .utils import process_image
from .camera import Camera

import cv2

"""
ProcessedCamera
This is virtual camera: it takes in a Camera class (either an actual Camera or RemoteCamera camera)
and processes the frames it receives, storing them in a new buffer. This new buffer can be read
using the same interface as the original camera.

Raw Camera usage:
with Camera() as camera:
    with ProcessedCamera(camera) as camera_processed:
        cv2.imshow("processed video", camera_processed.read())

RemoteCamera usage:
stream = RemoteCamera(ip)
with ProcessedCamera(stream) as camera_processed:
    ...
"""


class ProcessedCamera(Camera):
    def __init__(self, camera: Camera) -> None:
        self.camera = camera
        self.stop = False

        self.buffer = None
        self.lock = Lock()

        # Start thread that proccesses frames from the buffer
        self.t = Thread(target=self.processor, args=[])
        self.t.start()

    # Entering the context of a camera "with Camera() as cam"
    def __enter__(self):
        return self

    # When exiting the context of the camera, stop the worker threads
    def __exit__(self, type, value, traceback):
        self.stop = True
        self.t.join()

    # Worker for processing frames from the camera (resize + gauss + canny)
    def processor(self):
        while not self.stop:
            self.camera.ev.wait()
            img = self.camera.read()
            proc = process_image(img)
            cv2.imshow("og", img)
            cv2.waitKey(1)

            self.lock.acquire()
            self.buffer = np.copy(proc)
            self.lock.release()

            cv2.imshow("s", self.buffer)
            cv2.waitKey(1)

    def read(self):
        frame = []
        while frame is None or len(np.shape(frame)) == 0:
            self.lock.acquire()
            frame = np.copy(self.buffer)
            self.lock.release()
            if frame is None or len(np.shape(frame)) == 0:
                time.sleep(0.1)
        return frame
