import time
import cv2

from ..angle_sensor import AngleSensor
from common.camera import Camera


"""
Angle Sensor - Test Program
Creates an Angle Sensor and prints the results of the sensor to the console.
"""


def main():
    camera = Camera()
    with camera as cam:
        sensor = AngleSensor(cam)
        while True:
            print(sensor.run())
            time.sleep(0.05)


if __name__ == "__main__":
    main()
