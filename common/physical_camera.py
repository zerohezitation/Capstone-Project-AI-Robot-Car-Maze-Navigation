
import cv2
from threading import Thread

from common.camera import Camera


"""
PhysicalCamera
This class reads frames from the device's attached camera, and stores them in a buffer.
We do this because:
1) it takes a non-trivial amount of time to read from the camera and
2) multiple things may want to use the camera at the same time
By constantly updating the buffer, there is always a frame available to read, and we won't
bottleneck the other parts of the pipeline waiting for I/O.

Create a camera:
with PhysicalCamera() as camera:
    # Use camera here
"""


class PhysicalCamera(Camera):

    # Camera constructor
    def __init__(self, cam_port=-1) -> None:
        super().__init__()

        # Start thread that takes snapshots and writes them to buffer
        self.t = Thread(
            target=self.camera_reader, args=(cam_port,))
        self.t.start()

    # Worker for reading raw frames from the camera
    def camera_reader(self, cam_port: int):

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
                super().write(image)

        # release the video stream - otherwise we won't be able to start up again without restarting the pi
        cam.release()
