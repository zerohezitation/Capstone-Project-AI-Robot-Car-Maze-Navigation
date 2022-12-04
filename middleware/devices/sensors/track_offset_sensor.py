import numpy as np
import time

from common.physical_camera import Camera
from common.processed_camera import ProcessedCamera
from .ai_sensor import AiSensor

"""
TrackOffsetSensor
This sensor takes frames from the camera feed and inputs them into the 
specified AI model. We use the output of this model to return a value
corresponding to how "offset" the robot is from the track

"offset_right": The robot needs to turn left to correct itself
"straight": The robot can go straight ahead
"offset_left": The robot needs to turn right to correct itself
"none": The robot doesn't see the track, or isn't confident enough to make a determination

You can run this file standalone to test out the sensor without running the middleware:

python3 -m middleware.devices.sensors.track_offset_sensor
"""


class TrackOffsetSensor(AiSensor):
    def __init__(self, camera: Camera, model_path="./model.tflite"):
        super().__init__(camera, model_path)
        self.name = "ai"

    # Convert output tensor to prediction
    def map_prediction_to_output(self, output_tensor):
        idx = np.argmax(output_tensor)
        # print(idx, "p", output_tensor)
        # std = np.std(output_tensor)
        if idx == -1 or output_tensor[idx] < 0.9:
            idx = -1

        if idx == 0:
            return "offset_right"
        elif idx == 1:
            return "straight"
        elif idx == 2:
            return "offset_left"

        return "none"

    # Read the current prediction from the buffer
    def run(self) -> str:
        output_tensor = super().run()
        return self.map_prediction_to_output(output_tensor)


if __name__ == "__main__":
    camera = Camera()
    with camera as cam:
        with ProcessedCamera(cam) as cam_p:
            sensor = TrackOffsetSensor(cam_p)
            while True:
                print(sensor.run())
                time.sleep(0.1)
