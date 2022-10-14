import websockets
import asyncio
import json
import re
import threading
import time
import sys
import getopt

import socket
from camera import Camera
from ai_sensor import AiSensor
from angle_sensor import AngleSensor
from distance_sensor import DistanceSensor
from motors import Motors

#HOST = socket.gethostname()
HOST = "192.168.16.1"
PORT = 8124

LEFT_WHEEL_PORT = 3
RIGHT_WHEEL_PORT = 5

conn1 = None

SENSOR_POLLING_TIME = 500  # polling rate in milliseconds

sensors_dict = {
    "sensors": [{
        "name": "distance",
        "id": 1,
        "value": 50
    },
        #     {
        #     "name": "ai",
        #     "id": 2,
        #     "value": "straight"
        # },
        {
        "name": "angle",
        "id": 3,
        "value": 0
    }]
}

motor_dict = {
    "servos": [
        {
            "isTurn": False,
            "servoId": 3,
            "servoSpeed": 0
        },
        {
            "isTurn": False,
            "servoId": 5,
            "servoSpeed": 0
        }]
}

# Periodically update the server with new sensor values


async def send(websocket):
    while True:
        try:
            json_response = json.dumps(sensors_dict)
            print("Send > " + json_response)
            websocket.send((json_response + "\r\n").encode())
            await asyncio.sleep(SENSOR_POLLING_TIME / 1000)
        except:
            return False

# Listen to all incoming messages from the server
# Used for a websocket connection


async def listen_websocket(websocket):
    global motor_dict
    async for message in websocket:
        print(message)
        print("Recv < " + message)
        motor_dict = json.loads(message)
        print(motor_dict)

# Listen to all incoming messages from the server
# Used for a plain socket connection


async def listen_socket(socket):
    global motor_dict
    while True:
        try:
            message = socket.recv(65535)
            print(str(message))
            dec = message.decode()
            print("Recv < " + dec)
            if (dec == ""):
                return False
            lastjson = re.split("\r\n", dec)[-2]
            motor_dict = json.loads(lastjson)
            await asyncio.sleep(0.05)
        except:
            await asyncio.sleep(0)


# Asynchronously and concurrently handle incoming/outgoing messages
async def handler(websocket):
    await asyncio.gather(
        send(websocket),
        listen_socket(websocket)
    )

# Start TCP Server that waits for VIPLE Wifi clients to connect to it


async def setup_server():
    global conn1
    server_socket = socket.socket()
    try:
        print("Starting Middleware Server on " + HOST + ":" + str(PORT))

        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        while True:
            print("Waiting for connection...")
            conn, address = server_socket.accept()
            conn.setblocking(0)
            conn1 = conn
            print("Successful connection with " + str(address))
            await handler(conn)
            print("End of connction with " + str(address))
            print("--------------------------------------")

    finally:
        if conn1 is not None:
            conn1.close()
        if server_socket is not None:
            server_socket.close()


# Open the connection with the server via a websocket
# Start listening to messages sent from server, and periodically send sensor values back to server
async def setup_websocket_connection():
    print(f"Opening websocket connection with \'{HOST}:{PORT}\'...")
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        print(f"Successfully connected to \'{HOST}:{PORT}\'.")
        await handler(websocket)

# Periodically get the updated sensor values and store them in the dictionary


def update_sensors():
    camera = Camera()
    with camera as cam:
        sensors = [
            DistanceSensor(),
            # AiSensor(cam),
            AngleSensor(cam)
        ]

        while True:
            for (idx, sensor) in enumerate(sensors):
                sensors_dict["sensors"][idx]["value"] = sensor.run()
            print(sensors_dict)
            time.sleep(0.5)

# TODO spawn a new thread that updates the motor power values based on messages from the server


def update_motors():
    motors = Motors()
    while True:
        speed = abs(motor_dict["servos"][0]["servoSpeed"])
        speeds = (motor_dict["servos"][0]["servoSpeed"],
                  motor_dict["servos"][1]["servoSpeed"])
        motors.set_speed(new_speeds=speeds)
        time.sleep(0.05)

# Main loop


def main(argv):
    global HOST, PORT
    # try:
    #    # Attempt to parse the command line arguments
    #    opts, args = getopt.getopt(argv, "h:p:", ["host", "port"])
    # except getopt.GetoptError:
    #    # If parsing was unsuccessful, show the proper usage and exit
    #    print("main.py -h <HostIPAddress> -p <Port>")
    #    sys.exit(2)

    # Take the appropriate action for each command line argument
    # for opt, arg in opts:
    #    print(opts)
    #    if opt == "-h":
    #        HOST = arg
    #    if opt == "-p":
    #        PORT = int(arg)

    t1 = threading.Thread(target=update_sensors, args=[])
    t1.start()
    t2 = threading.Thread(target=update_motors, args=[])
    t2.start()

    try:
        # open the websocket connection to start sending/receiving from the server
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(setup_server())
        loop.run_forever()
    finally:
        print("Closing connection.")
        if conn1 is not None:
            conn1.close()


if __name__ == "__main__":
    main(sys.argv[1:])
