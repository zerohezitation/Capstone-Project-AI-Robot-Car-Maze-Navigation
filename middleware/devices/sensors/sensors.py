from threading import Thread, Lock
import time
from common.buffer import Buffer
import logging

from common.physical_camera import Camera
from middleware.devices.sensors.ai_sensor import AiSensor
from middleware.devices.sensors.angle_sensor import AngleSensor
from middleware.devices.sensors.distance_sensor import DistanceSensor
from middleware.devices.sensors.track_offset_sensor import TrackOffsetSensor

"""
Sensors
This class packages up all of the robots sensors, updating a dictionary
of sensors values that are to be send to the client.
"""


class Sensors:

    def __init__(self, sensors) -> None:
        self.buffer_lock = Lock()
        self.sensors = sensors

        self.stop = False

        # Keep a dictionary of the sensor values that we can send to the client
        self.sensors_dict = {"sensors": []}
        for idx, sensor in enumerate(sensors):
            id = idx + 1
            self.sensors_dict["sensors"] \
                .append({"id": id, "name": sensor.name, "value": None})

        # Start the threads for updating the sensor values and motor target speeds
        self.t = Thread(target=self.update, args=[])
        self.t.start()

    # Entering the context of the motor object
    def __enter__(self):
        return self

    # When exiting the context of the motor, stop worker thread
    def __exit__(self, type, value, traceback):
        self.stop = True

        # First, stop the worker thread
        if self.t is not None:
            logging.debug(f"Waiting for Sensors worker thread to finish...")
            self.t.join()

        # Next, stop all of the sensors in the configuration
        # This is mostly to signal to each sensor that they need to stop their worker thread(s)
        logging.debug(f"Stopping all sensors...")
        for sensor in self.sensors:
            sensor.stop()
        logging.debug(f"Sensors is exiting.")

    def update(self):
        # Poll each sensor for an updated value, and store it in the buffer
        while not self.stop:
            for (idx, sensor) in enumerate(self.sensors):
                sensor_value = sensor.run()
                with self.buffer_lock:
                    self.sensors_dict["sensors"][idx]["value"] = sensor_value

    def read(self):
        # Read the current value of the sensor dictionary
        sensors_dict = None
        with self.buffer_lock:
            sensors_dict = self.sensors_dict
        return sensors_dict


# Create a sensor configuration that only has the AI sensor.
def create_ai_sensor_config(camera: Camera) -> Sensors:
    sensors_list = [
        # DistanceSensor(),
        TrackOffsetSensor(camera),
        # AngleSensor(camera)
    ]
    sensors = Sensors(sensors_list)
    return sensors
