import numpy as np
import time
import logging
import cv2
from common.buffer import Buffer


class Camera:
    def __init__(self) -> None:
        self.buffer = Buffer(None)
        self.stop = False
        self.t = None
        self.name = "Camera"

    # Entering the context of a camera "with Camera() as cam"
    def __enter__(self):
        return self

    # When exiting the context of the camera, stop the worker threads
    def __exit__(self, error_type, value, traceback):
        self.stop = True
        name = type(self).__name__
        if self.t is not None:
            logging.debug(f"Waiting for {name} worker thread to finish...")
            self.t.join()
        logging.debug(f"{name} is exiting.")

    def write(self, image):
        self.buffer.write(image)
        # cv2.imshow("image in camera", image)

    def read(self):
        current_value = None
        while True:
            # Read the most recent frame from the buffer
            current_value = self.buffer.read()

            if current_value is not None:
                # We get a valid frame from the buffer, return it
                break

            # If the buffer was None, a valid frame hasn't been written to the buffer yet
            # Wait a bit for a valid frame to get written and check again
            # We can sleep for a relatively long amount of time because this will only happen when you first start up the camera
            time.sleep(0.1)

        self.buffer.publish_event.clear()
        return current_value
