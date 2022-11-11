from threading import Thread

from .utils import process_image
from common.camera import Camera

"""
ProcessedCamera
This is virtual camera: it takes in a Camera class (either a PhysicalCamera or RemoteCamera camera)
and processes the frames it receives, storing them in a new buffer. This new buffer can be read
using the same interface as the original camera.

Camera usage:
with PhysicalCamera() as camera:
    with ProcessedCamera(camera) as camera_processed:
        cv2.imshow("processed video", camera_processed.read())
"""


class ProcessedCamera(Camera):
    def __init__(self, camera: Camera) -> None:
        super().__init__()
        self.camera = camera

        # Start thread that proccesses frames from the buffer
        self.t = Thread(target=self.processor, args=[])
        self.t.start()

    # Worker for processing frames from the camera (resize + gauss + canny)
    def processor(self):
        while not self.stop:
            img = self.camera.read()
            proc = process_image(img)
            super().write(proc)
