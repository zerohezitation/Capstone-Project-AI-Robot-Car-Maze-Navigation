import RPi.GPIO as GPIO
import time
from threading import Thread, Lock
import logging

from common.buffer import Buffer

from .sensor import Sensor

"""
Distance Sensor
Starts a thread that periodically checks the current distance, and stores it in a buffer
Exposes a "run" method that acquires the distance from the buffer.

You can run this file standalone to test out the sensor without running the middleware:

python3 -m middleware.devices.sensors.distance_sensor
"""


class DistanceSensor(Sensor):
    t = None
    echo = 5
    trig = 6

    def __init__(self, echo=5, trig=6) -> None:
        super().__init__()
        self.name = "distance"

        # Set the pins for GPIO
        self.echo = echo
        self.trig = trig
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

        # Start a thread that constantly updates the distance buffer
        self.buffer = Buffer(-1)
        self.t = Thread(target=self.get_distance, args=())
        self.t.start()

    # Worker for checking the ultrasonic distance sensor and storing value in buffer
    def get_distance(self):
        while True:
            GPIO.output(self.trig, True)
            time.sleep(0.00001)
            GPIO.output(self.trig, False)

            while GPIO.input(self.echo) == False:
                start = time.time()

            while GPIO.input(self.echo) == True:
                end = time.time()

            sig_time = end-start
            distance = sig_time / 0.000058

            self.buffer.write(distance)

            time.sleep(0.25)  # update distance 4 times per second

    # Get the value of the distance sensor (read the most recent value of buffer)
    def run(self):
        return self.buffer.read()

    def stop(self):
        self.sentinel = True
        name = type(self).__name__
        if self.t is not None:
            logging.debug(f"Waiting for {name} worker thread to finish...")
            self.t.join()
        logging.debug(f"{name} is exiting.")


if __name__ == "__main__":
    sensor = DistanceSensor()
    while True:
        print(sensor.run())
        time.sleep(0.1)
