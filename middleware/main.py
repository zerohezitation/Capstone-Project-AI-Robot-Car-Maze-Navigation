import socket
import asyncio
import json
import re
import sys
import struct
import fcntl
#import websockets

from common.camera import Camera
from middleware.devices.sensors.sensors import Sensors, create_ai_sensor_config
from middleware.devices.motors import Motors


PORT = 8124
SENSOR_POLLING_TIME = 250  # polling rate in milliseconds

connection = None


def get_ip(interface: str = "wlan0") -> str:
    # Get the IP address of the specified interface
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_iface = struct.pack('256s', interface.encode('utf_8'))
    packed_addr = fcntl.ioctl(sock.fileno(), 0x8915, packed_iface)[20:24]
    return socket.inet_ntoa(packed_addr)


async def send(socket, sensors: Sensors) -> None:
    # Periodically update the server with new sensor values
    while True:
        try:
            json_response = json.dumps(sensors.read())
            print("Send > " + json_response)
            socket.send((json_response + "\r\n").encode())
            await asyncio.sleep(SENSOR_POLLING_TIME / 1000)
        except:
            return False


async def listen(socket, motors: Motors) -> None:
    # Listen to all incoming messages from the server
    # Used for a plain socket connection
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

            speeds = [motor_dict["servos"][i]["servoSpeed"]
                      for i in range(len(motor_dict["servos"]))]
            motors.set_target_speed(speeds)

            await asyncio.sleep(0.05)
        except:
            await asyncio.sleep(0)


async def connection_handler(socket, sensors: Sensors, motors: Motors) -> None:
    # Asynchronously and concurrently handle incoming/outgoing messages
    await asyncio.gather(
        send(socket, sensors),
        listen(socket, motors)
    )


async def setup_server(sensors: Sensors, motors: Motors):
    # Start TCP Server that waits for VIPLE Wifi clients to connect to it
    global connection
    server_socket = socket.socket()
    host = get_ip()

    try:
        print("Starting Middleware Server on " + host + ":" + str(PORT))

        server_socket.bind((host, PORT))
        server_socket.listen(1)
        while True:
            print("Waiting for connection...")
            conn, address = server_socket.accept()
            conn.setblocking(0)
            connection = conn
            print("Successful connection with " + str(address))
            await connection_handler(conn, sensors, motors)
            print("End of connction with " + str(address))
            print("--------------------------------------")

    finally:
        if connection is not None:
            connection.close()
        if server_socket is not None:
            server_socket.close()


def main(argv):
    motors = Motors()
    camera = Camera()
    with camera as cam:
        sensors = create_ai_sensor_config(cam)

        # Start the server and start listening for connections on the main thread
        try:
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(setup_server(sensors, motors))
            loop.run_forever()
        finally:
            print("Closing connection.")
            if connection is not None:
                connection.close()


# Deprecated websocket methods

# async def listen_websocket(websocket):
#     # Listen to all incoming messages from the server
# # Used for a websocket connection
#     global motor_dict
#     async for message in websocket:
#         print(message)
#         print("Recv < " + message)
#         motor_dict = json.loads(message)
#         print(motor_dict)

# Open the connection with the server via a websocket
# Start listening to messages sent from server, and periodically send sensor values back to server
# async def setup_websocket_connection():
#     print(f"Opening websocket connection with \'{HOST}:{PORT}\'...")
#     async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
#         print(f"Successfully connected to \'{HOST}:{PORT}\'.")
#         await handler(websocket)

# Periodically get the updated sensor values and store them in the dictionary


if __name__ == "__main__":
    main(sys.argv[1:])
