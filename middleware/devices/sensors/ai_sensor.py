# import tflite_runtime.interpreter as tflite
import tensorflow.lite as tflite
import cv2
import numpy as np
import time

from .sensor import Sensor
from common.camera import Camera
from common.utils import process_image


class AiSensor(Sensor):
    cam = None

    state = 2
    next_state = 0
    next_state_count = 0

    interpreter = None

    def __init__(self, camera: Camera, model_path="./model.tflite") -> None:
        super().__init__()
        self.name = "ai"

        self.cam = camera
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.state = 2

    # Convert output tensor to prediction
    def map_prediction_to_output(self, output_tensor):
        idx = np.argmax(output_tensor)
        #print(idx, "p", prediction[idx])
        std = np.std(output_tensor)
        if (std < 0.3):  # prediction[idx] < 0.9):  # or ):
            idx = -1

        if idx != self.state:
            if self.next_state == idx:
                self.next_state_count += 1
                if self.next_state_count > 5:  # some threshhold to switch between states
                    self.state = self.next_state
                    self.next_state_count = 0
            else:
                self.next_state_count -= 1
                if self.next_state_count <= 0:
                    self.next_state = idx
                    self.next_state_count = 0
        else:
            if self.next_state_count > 0:
                self.next_state_count -= 1

        # print(self.state, self.next_state, self.next_state_count)

        idx = self.state
        # print(prediction[idx])

        if (idx == 0):
            return "none"
        elif (idx == 1):
            return "left"
        elif (idx == 2):
            return "offset_left"
        elif (idx == 3):
            return "straight"
        elif (idx == 4):
            return "offset_right"
        elif (idx == 5):
            return "right"
        else:
            return "none"

    def run(self):
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        # Read a frame from the camera
        image = self.cam.read_p()

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

        # Convert output tensor to predictor
        return self.map_prediction_to_output(output_data[0])
