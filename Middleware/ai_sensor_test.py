from ai_sensor import AiSensor
from camera import Camera
import time

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
            time.sleep(0.001)


if __name__ == "__main__":
    main()
