import time
from smbus2 import SMBus
from threading import Lock, Thread
from typing import Tuple

from numpy import double

# Constants for addressing the I2C bus
I2C_ADDRESS = 0x18
I2C_COMMAND = 0xff

# Motor command constants
# Send these commands on the I2C to control the motors/lights

# Step 1) Set the speed of the left/right motors
# You can't control the four motors independently, only the left and right sides
I2C_LEFT_SPEED_SLOW = 0x2605  # minimum left side speed
I2C_LEFT_SPEED_FAST = 0x260A  # maximum left side speed
I2C_RIGHT_SPEED_SLOW = 0x2705  # minimum right side speed
I2C_RIGHT_SPEED_FAST = 0x270A  # maximum right side speed

# Step 2) Control the direction of the motors
I2C_STOP = 0x210A  # all motors stop
I2C_FORWARD = 0x220A  # left and right move forward
I2C_BACKWARD = 0x230A  # left and right move backward
I2C_LEFT = 0x240A  # left moves backward, right moves forward
I2C_RIGHT = 0x250A  # right moves backward, left moves forward

# Headlight controls
I2C_HEADLIGHT_LEFT_OFF = 0x3600
I2C_HEADLIGHT_LEFT_ON = 0x3601
I2C_HEADLIGHT_RIGHT_OFF = 0x3700
I2C_HEADLIGHT_RIGHT_ON = 0x3701


class Motors:
    bus = None
    speeds = (0, 0)
    buffer = ()
    motor_speed_buffer_lock = None
    t = None

    motor_hex_base = 0x2600  # base value of hex I2C commands
    motors = [motor_hex_base, motor_hex_base + 0x100]
    min_speed = 0x0  # 0x1

    motor_dict = {}
    motor_dict_buffer_lock = None

    # Motors constructor
    def __init__(self, ports=(3, 5)) -> None:
        self.bus = SMBus(1)
        time.sleep(1)  # You need to wait for the I2C bus to initialize

        self.motor_dict_buffer_lock = Lock()
        self.motor_dict = {
            "servos": [
                {
                    "isTurn": False,
                    "servoId": ports[0],
                    "servoSpeed": 0
                },
                {
                    "isTurn": False,
                    "servoId": ports[1],
                    "servoSpeed": 0
                }]
        }

        self.motor_speed_buffer_lock = Lock()
        self.t = Thread(target=self.update_motor_speeds, args=())
        self.t.start()

        self.headlights()

    # Send a command to the I2C bus
    def send_command(self, word) -> None:
        self.bus.write_word_data(I2C_ADDRESS, I2C_COMMAND, word)
        # IMPORTANT!!!!!!!!!
        # If you sent commands too quickly they will be lost, and your motors will not do what you tell them to!
        # Below is the minimum amount of time to wait but you should probably wait even longer than this
        time.sleep(0.001)

    # Constantly read the motor speed target, and send I2C commands to match the target
    def update_motor_speeds(self) -> None:
        while True:
            # Read the current speed target from the buffer
            self.motor_speed_buffer_lock.acquire()
            new_powers = self.buffer
            new_speeds = self.speeds
            self.buffer = None
            self.motor_speed_buffer_lock.release()

            # If new_powers is None, nothing has tried to write to the buffer since it was last reset, so maintain current power
            if new_powers is not None:
                # If there was new_powers, send commands for L and R motors to match speed
                for power in new_powers:
                    self.send_command(power)
                    # You need to wait to make sure that the I2C bus doesn't eat up one of the commands!!!!!!!!
                    time.sleep(0.05)

                # Now that we've set the magnitude of the speed, we need to set the direction and start the motors moving
                l, r = new_speeds
                command = None
                if(l > 0 and r > 0):
                    command = I2C_FORWARD
                elif(l < 0 and r < 0):
                    command = I2C_BACKWARD
                elif(l == 0 and r == 0):
                    command = I2C_STOP
                elif(l <= 0 and r >= 0):
                    command = I2C_LEFT
                elif(l >= 0 and r <= 0):
                    command = I2C_RIGHT
                self.send_command(command)

            time.sleep(0.01)

    # Conver the power from double to the hex value expected by the I2C bus
    def convert_speeds_to_commands(self, speeds: Tuple[double, double]) -> Tuple[int, int]:
        powers = []
        for idx, speed in enumerate(speeds):
            # Get the magnitude of the speed and convert from range [-1, 1] to [0, 10]
            offset = abs(int(speed * 10))
            motor = self.motors[idx]
            power = motor + self.min_speed + offset
            powers.append(power)
        return tuple(powers)

    # Set the speed target for the motors
    def set_target_speed(self, new_speeds: Tuple[double, double]) -> None:
        if self.speeds != new_speeds:
            powers = self.convert_speeds_to_commands(new_speeds)

            self.motor_speed_buffer_lock.acquire()
            self.speeds = new_speeds
            self.buffer = powers
            self.motor_speed_buffer_lock.release()

    # Set the state of the headlights
    def headlights(self, state=True):
        commands = (I2C_HEADLIGHT_LEFT_ON, I2C_HEADLIGHT_RIGHT_ON)
        if not state:
            commands = (I2C_HEADLIGHT_LEFT_OFF, I2C_HEADLIGHT_RIGHT_OFF)

        for command in commands:
            self.send_command(command)
            time.sleep(1)
