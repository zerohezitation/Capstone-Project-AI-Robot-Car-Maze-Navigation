import time
from smbus2 import SMBus
from threading import Lock, Thread

I2C_ADDRESS = 0x18
I2C_COMMAND = 0xff

# Motor
I2C_STOP = 0x210A
I2C_FORWARD = 0x220A
I2C_BACKWARD = 0x230A
I2C_LEFT = 0x240A
I2C_RIGHT = 0x250A

I2C_LEFT_SPEED_SLOW = 0x2605
I2C_LEFT_SPEED_FAST = 0x260A
I2C_RIGHT_SPEED_SLOW = 0x2705
I2C_RIGHT_SPEED_FAST = 0x270A


I2C_HEADLIGHT_LEFT_OFF = 0x3600
I2C_HEADLIGHT_LEFT_ON = 0x3601
I2C_HEADLIGHT_RIGHT_OFF = 0x3700
I2C_HEADLIGHT_RIGHT_ON = 0x3701


class Motors:
    bus = None
    speeds = (0, 0)
    buffer = ()
    lock = None
    t = None

    motor_hex_base = 0x2600
    motors = [motor_hex_base, motor_hex_base + 0x100]
    min_speed = 0x1

    def __init__(self) -> None:
        self.bus = SMBus(1)
        time.sleep(1)

        self.lock = Lock()
        self.t = Thread(target=self.update_motor_speeds, args=())
        self.t.start()

    def write_word(self, word) -> None:
        self.bus.write_word_data(I2C_ADDRESS, I2C_COMMAND, word)
        time.sleep(0.001)

    def update_motor_speeds(self):
        while True:
            self.lock.acquire()
            new_powers = self.buffer
            new_speeds = self.speeds
            self.buffer = None
            self.lock.release()

            if new_powers is not None:
                for power in new_powers:
                    self.write_word(power)

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
                self.write_word(command)

            time.sleep(0.01)

    def convert_speeds_to_commands(self, speeds):
        powers = []
        for idx, speed in enumerate(speeds):
            offset = abs(int(speed * 10))
            motor = self.motors[idx]
            power = motor + self.min_speed + offset
            powers.append(power)
        return tuple(powers)

    def set_speed(self, new_speeds):
        if self.speeds != new_speeds:
            powers = self.convert_speeds_to_commands(new_speeds)

            self.lock.acquire()
            self.speeds = new_speeds
            self.buffer = powers
            self.lock.release()
