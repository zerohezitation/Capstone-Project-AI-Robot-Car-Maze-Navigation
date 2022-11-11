import tflite_runtime.interpreter as tflite
#import tensorflow.lite as tflite
import cv2
import numpy as np
import time
from threading import Lock, Thread, Event
import logging

from .sensor import Sensor
from common.physical_camera import Camera
from common.utils import process_image
from common.buffer import Buffer

"""
AiSensor
This class reads images from the Camera, and inputs them into the
specified Tensorflow Lite model. It will output the raw output tensor of
the model.
"""


class AiSensor(Sensor):
    cam = None
    interpreter = None

    def __init__(self, camera: Camera, model_path="./model.tflite") -> None:
        super().__init__()
        self.name = "ai"
        self.sentinel = False

        self.cam = camera
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.buffer = Buffer()
        self.t = Thread(target=self.worker, args=[])
        self.t.start()

    def worker(self) -> None:
        while not self.sentinel:
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()

            # Read a frame from the camera
            image = self.cam.read()

            # Convert to the shape the model is expecting
            image = image.astype(np.float32)
            image = image[np.newaxis, :, :, np.newaxis]

            # Set the AI model input
            self.interpreter.set_tensor(
                input_details[0]["index"], image)

            # Invoke the model on the frame
            self.interpreter.invoke()

            # Read the AI model output
            output_data = self.interpreter.get_tensor(
                output_details[0]['index'])

            # Write output tensor to the output buffer
            self.buffer.write(output_data[0])

    def run(self):
        return self.buffer.read()

    def stop(self):
        self.sentinel = True
        name = type(self).__name__
        if self.t is not None:
            logging.debug(f"Waiting for {name} worker thread to finish...")
            self.t.join()
        logging.debug(f"{name} is exiting.")
