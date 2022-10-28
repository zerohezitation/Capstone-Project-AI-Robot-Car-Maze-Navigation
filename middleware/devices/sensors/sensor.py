from abc import ABC, abstractmethod

# Abstract class that all other sensors inherit


class Sensor(ABC):

    @abstractmethod
    def run(self):
        pass
