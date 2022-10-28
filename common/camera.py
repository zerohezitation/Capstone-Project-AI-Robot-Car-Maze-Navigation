
import cv2
from threading import Thread, Lock, Event
import numpy as np
import time

from .utils import process_image


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
    raw_camera_thread = None
    processor_thread = None
    current_frame = None
    processed_frame = None
    raw_frame_buffer_lock = None
    processed_frame_buffer_lock = None
    stop = False

    # Camera constructor
    def __init__(self, cam_port=-1) -> None:
        self.stop = False
        self.raw_frame_buffer_lock = Lock()
        self.processed_frame_buffer_lock = Lock()

        ev = Event()

        # Start thread that takes snapshots and writes them to buffer
        self.raw_camera_thread = Thread(
            target=self.camera_reader, args=(cam_port, ev))
        self.raw_camera_thread.start()

        # Start thread that proccesses frames from the buffer
        self.processor_thread = Thread(target=self.processor, args=(ev,))
        self.processor_thread.start()

    # Entering the context of a camera "with Camera() as cam"
    def __enter__(self):
        return self

    # When exiting the context of the camera, stop the worker threads
    def __exit__(self, type, value, traceback):
        self.stop = True
        self.raw_camera_thread.join()
        self.processor_thread.join()

    # Worker for reading raw frames from the camera
    def camera_reader(self, cam_port: int, ev: Event):

        # use V4L2 backend to be able to adjust fraame rate >15fps
        cam = cv2.VideoCapture(cam_port, cv2.CAP_V4L2)
        # 320x240 at 25fps - run "v4l2-ctl --list-formats" to determine available formats
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cam.set(cv2.CAP_PROP_FPS, 25)
        # lower buffer size to get immediate results
        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # continually get frames from camera and store them in the buffer
        while not self.stop:
            result, image = cam.read()
            if result:
                self.raw_frame_buffer_lock.acquire()
                self.current_frame = image
                self.raw_frame_buffer_lock.release()
                ev.set()
            time.sleep(0.05)

        # release the video stream - otherwise we won't be able to start up again without restarting the pi
        cam.release()

    # Worker for processing frames from the camera (resize + gauss + canny)
    def processor(self, ev: Event):
        while not self.stop:
            ev.wait()
            img = self.read()
            proc = process_image(img)
            #cv2.imshow("proc", img)
            self.processed_frame_buffer_lock.acquire()
            self.processed_frame = proc
            self.processed_frame_buffer_lock.release()
            time.sleep(0.05)

    # Read a raw frame from the buffer (no processing)
    def read(self):
        frame = []
        while frame is None or len(frame) == 0:
            self.raw_frame_buffer_lock.acquire()
            #frame = np.copy(self.current_frame)
            frame = self.current_frame
            self.raw_frame_buffer_lock.release()

            # If the frame from the buffer is None, the camera hasn't started up yet
            # Wait a little while for it to warm up
            if frame is None or len(frame) == 0:
                time.sleep(0.1)
        return frame

    # Read a processed frame from the buffer (resize + gauss + canny)
    def read_p(self):
        frame = []
        while frame is None or len(frame) == 0:
            self.processed_frame_buffer_lock.acquire()
            #frame = np.copy(self.current_frame)
            frame = self.processed_frame
            self.processed_frame_buffer_lock.release()
            if frame is None or len(frame) == 0:
                time.sleep(0.1)
        return frame
