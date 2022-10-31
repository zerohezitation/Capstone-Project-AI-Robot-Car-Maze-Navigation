from threading import Thread, Lock
import time

from common.camera import Camera
from middleware.devices.sensors.ai_sensor import AiSensor
from middleware.devices.sensors.angle_sensor import AngleSensor
from middleware.devices.sensors.distance_sensor import DistanceSensor

"""
Sensors
This class packages up all of the robots sensors, updating a dictionary
of sensors values that are to be send to the client.
"""


class Sensors:

    def __init__(self, sensors) -> None:
        self.buffer_lock = Lock()
        self.sensors = sensors

        # Keep a dictionary of the sensor values that we can send to the client
        self.sensors_dict = {"sensors": []}
        for idx, sensor in enumerate(sensors):
            id = idx + 1
            self.sensors_dict["sensors"] \
                .append({"id": id, "name": sensor.name, "value": None})

        # Start the threads for updating the sensor values and motor target speeds
        self.t = Thread(target=self.update_sensors, args=[])
        self.t.start()

    def update(self):
        # Poll each sensor for an updated value, and store it in the buffer
        self.buffer_lock.acquire()
        for (idx, sensor) in enumerate(self.sensors):
            self.sensors_dict["sensors"][idx]["value"] = sensor.run()
        self.buffer_lock.release()

    def update_sensors(self):
        # Continuously poll the sensors for updated values
        while True:
            self.update()
            # print(self.sensors_dict)
            time.sleep(0.05)

    def read(self):
        # Read the current sensor values from the buffer
        values = None
        self.buffer_lock.acquire()
        values = self.sensors_dict
        self.buffer_lock.release()
        return values


# Create a sensor configuration that only has the AI sensor.
def create_ai_sensor_config(camera: Camera) -> Sensors:
    sensors_list = [
        # DistanceSensor(),
        AiSensor(camera),
        # AngleSensor(camera)
    ]
    sensors = Sensors(sensors_list)
    return sensors
