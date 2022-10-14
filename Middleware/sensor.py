from abc import ABC, abstractmethod


class Sensor(ABC):
    @abstractmethod
    def run(self):
        pass
