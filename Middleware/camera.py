
import cv2
from threading import Thread, Lock, Event
from utils import *
import numpy as np
import time


"""
Camera Sensor

Create a camera:
cam = Camera()
with cam as c:
    # Use c here

Read a raw camera frame:
frame = cam.read()

Read a processed camera frame:
p_frame = cam.read_p()
"""


class Camera:
    t = None
    t2 = None
    current_frame = None
    processed_frame = None
    lock = None
    lock2 = None
    stop = False

    def __init__(self, cam_port=-1) -> None:
        self.stop = False
        self.lock = Lock()
        self.lock2 = Lock()

        ev = Event()

        # Start thread that takes snapshots and writes them to buffer
        self.t = Thread(target=self.run, args=(cam_port, ev))
        self.t.start()

        # Start thread that proccesses frames from the buffer
        self.t2 = Thread(target=self.processor, args=(ev,))
        self.t2.start()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop = True
        self.t.join()
        self.t2.join()

    def run(self, cam_port: int, ev: Event):

        cam = cv2.VideoCapture(cam_port, cv2.CAP_ANY)
        while not self.stop:
            result, image = cam.read()
            if result:
                self.lock.acquire()
                self.current_frame = image
                self.lock.release()
                ev.set()
            time.sleep(0.05)
        cam.release()

    # Read a raw frame from the buffer (no processing)
    def read(self):
        frame = []
        while frame is None or len(frame) == 0:
            self.lock.acquire()
            #frame = np.copy(self.current_frame)
            frame = self.current_frame
            self.lock.release()
            if frame is None or len(frame) == 0:
                time.sleep(0.1)
        return frame

    # Read a processed frame from the buffer (resize + gauss + canny)
    def read_p(self):
        frame = []
        while frame is None or len(frame) == 0:
            self.lock2.acquire()
            #frame = np.copy(self.current_frame)
            frame = self.processed_frame
            self.lock2.release()
            if frame is None or len(frame) == 0:
                time.sleep(0.1)
        return frame

    def processor(self, ev: Event):
        while not self.stop:
            ev.wait()
            img = self.read()
            img = canny(gauss(resize(img)))
            #cv2.imshow("proc", img)
            self.lock2.acquire()
            self.processed_frame = img
            self.lock2.release()
            time.sleep(0.05)
