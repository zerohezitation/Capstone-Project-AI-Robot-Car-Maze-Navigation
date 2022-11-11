from ..motors import Motors

"""
You can run this script to set motor parameters that currently aren't controllable
through the middleware, namely turning the headlights on/off, and setting the position
of the servo.

Usage:
python3 -m middleware.devices.test.motors_test
> servo 255
255
> servo 0
0
> servo 125
125
> headlights True
> headlights False
"""


def main():
    motors = Motors()
    while True:
        command = input("> ")
        args = command.split(" ")
        if args[0] == "servo":
            motors.set_servo_position(int(args[1]))
            print(motors.get_servo_position())
        if args[0] == "headlights":
            motors.headlights(True if args[1] == "True" else False)


if __name__ == "__main__":
    main()
