from abc import ABC, abstractmethod

"""
Sensor
Abstract class that all other sensor inherit from

run() should generally be a short-running task so that we can update the
sensors dictionary (see Sensors) as fast as possible. If a sensor needs to
perform a long-running task, it should spawn a thread that outputs the
value to a buffer that is read by run().
"""


class Sensor(ABC):

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass
