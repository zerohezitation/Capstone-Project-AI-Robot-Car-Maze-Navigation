from cv2 import waitKey
import tflite_runtime.interpreter as tflite
import cv2
import numpy as np
import time
from sensor import Sensor
from utils import *
from camera import Camera


class AiSensor(Sensor):
    cam = None

    state = 2
    next_state = 0
    next_state_count = 0

    interpreter = None

    def __init__(self, camera: Camera, model_path="./model.tflite") -> None:
        self.cam = camera
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.state = 2

    def map_prediction_to_output(self, prediction):
        idx = np.argmax(prediction)
        # print(prediction)
        std = np.std(prediction)
        # print(std)
        if (prediction[idx] < 0):  # or std < 10):
            return False

        if idx != self.state:
            if self.next_state == idx:
                self.next_state_count += 1
                if self.next_state_count > 4:  # some threshhold to switch between states
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

        #print(self.state, self.next_state, self.next_state_count)

        idx = self.state
        print(prediction[idx])

        if (idx == 0):
            return "left"
        elif (idx == 1):
            return "right"
        else:
            return "straight"

    def run(self):
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        result, image = self.cam.read()

        #result = True
        #image = cv2.imread('turn_left_img1.png')
        #image = cv2.imread('straight_img15.png')
        #image = cv2.imread('turn_right_img2.png')
        if result:
            image = canny(gauss(resize(image)))  # .astype(np.float32)
            cv2.imshow("img1", image)
            # cv2.waitKey(0)

            # time.sleep(2)

            # cv2.waitKey(0)
            # print(preprocess)
            image = np.repeat(image[:, :, np.newaxis], 3, axis=2)
            image = image[np.newaxis, :, :, :]

            self.interpreter.set_tensor(
                input_details[0]["index"], image.astype(np.float32))
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(
                output_details[0]['index'])
            # print(output_data)
            return self.map_prediction_to_output(output_data[0])
