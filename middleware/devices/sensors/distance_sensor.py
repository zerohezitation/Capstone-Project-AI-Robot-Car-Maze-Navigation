import RPi.GPIO as GPIO
import time
from threading import Thread, Lock

from .sensor import Sensor

"""
Distance Sensor
Starts a thread that periodically checks the current distance, and stores it in a buffer
Exposes a "run" method that acquires the distance from the buffer
"""


class DistanceSensor(Sensor):
    t = None
    buffer_lock = None
    distance = -1
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
        self.buffer_lock = Lock()
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

            # CM:
            distance = sig_time / 0.000058

            self.buffer_lock.acquire()
            self.distance = distance
            self.buffer_lock.release()
            time.sleep(0.05)

    # Get the value of the distance sensor (read the most recent value of buffer)
    def run(self):
        d = None
        self.buffer_lock.acquire()
        d = self.distance
        self.buffer_lock.release()
        return d
