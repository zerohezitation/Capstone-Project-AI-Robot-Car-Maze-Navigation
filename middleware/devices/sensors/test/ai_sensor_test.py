import time

from ..ai_sensor import AiSensor
from common.camera import Camera


"""
AI Sensor - Test Program
Creates an AI Sensor and prints the results of the sensor to the console.
"""


def main():
    camera = Camera()
    with camera as cam:
        sensor = AiSensor(camera)
        while True:
            print(sensor.run())
            time.sleep(0.1)


if __name__ == "__main__":
    main()
