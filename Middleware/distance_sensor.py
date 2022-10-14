from sensor import Sensor
import RPi.GPIO as GPIO
import time
from threading import Thread, Lock

"""
Distance Sensor
Starts a thread that periodically checks the current distance, and stores it in a buffer
Exposes a "run" method that acquires the distance from the buffer
"""


class DistanceSensor(Sensor):
    t = None
    lock = None
    distance = -1
    echo = 5
    trig = 6

    def __init__(self, echo=5, trig=6) -> None:
        self.echo = echo
        self.trig = trig
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

        self.lock = Lock()
        self.t = Thread(target=self.get_distance, args=())
        self.t.start()

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

            # round(distance,2)

            # inches:
            #distance = sig_time / 0.000148
            #print('Distance: {:0.2f} centimeters'.format(distance))
            self.lock.acquire()
            self.distance = distance
            self.lock.release()
            time.sleep(0.05)

    def run(self):
        d = None
        self.lock.acquire()
        d = self.distance
        self.lock.release()
        return d
