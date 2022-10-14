from camera import Camera
from angle_sensor import AngleSensor
import time
import cv2


"""
Angle Sensor - Test Program
Creates an Angle Sensor and prints the results of the sensor to the console.
"""


def main():
    camera = Camera()
    with camera as cam:
        while False:
            cv2.imshow("cam", cam.read())
            cv2.imshow("cam_p", cam.read_p())
            cv2.waitKey(1)
        sensor = AngleSensor(cam)
        while True:
            print(sensor.run())
            time.sleep(0.05)


if __name__ == "__main__":
    main()
