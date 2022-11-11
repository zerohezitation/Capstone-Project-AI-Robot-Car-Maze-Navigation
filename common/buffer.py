from threading import Lock, Event
import time
import numpy as np

"""
Buffer
"""


class Buffer:
    def __init__(self, initial_value=None) -> None:
        self.buffer = initial_value
        self.lock = Lock()
        self.publish_event = Event()

    # Read the current value of the buffer
    def read(self, timeout=None):
        current_value = None

        timed_out = not self.publish_event.wait(timeout)
        if timed_out:
            raise TimeoutError("A value was not published to the buffer within the timeout.")

        with self.lock:
            current_value = np.copy(self.buffer)
        self.publish_event.clear()
        return current_value

    # Update the value of the buffer
    def write(self, value):
        with self.lock:
            self.buffer = np.copy(value)
        self.publish_event.set()

    # Read from the buffer and write to it in a single critical section
    def read_and_write(self, value):
        current_value = None
        with self.lock:
            current_value = np.copy(self.buffer)
            self.buffer = value
        self.publish_event.set()
        return current_value
