import socket
import asyncio
import json
import re
import sys
import logging
from signal import SIGINT, SIGTERM
#import websockets

from common.camera import Camera
from common.processed_camera import ProcessedCamera
from common.utils import get_ip
from middleware.devices.sensors.sensors import Sensors, create_ai_sensor_config
from middleware.devices.motors import Motors
from middleware.streamer import Streamer


PORT = 8124
# rate in milliseconds at which we send updated sensor values to client
SENSOR_POLLING_TIME = 250

connection = None


async def send(socket, sensors: Sensors) -> None:
    # Periodically update the server with new sensor values
    while True:
        try:
            json_response = json.dumps(sensors.read())
            logging.debug(f"Send > {json_response}")
            socket.send((json_response + "\r\n").encode())
            await asyncio.sleep(SENSOR_POLLING_TIME / 1000)
        except:
            return False


async def listen(socket, motors: Motors) -> None:
    # Listen to all incoming messages from the server
    # Update the motors to match the speed we're sent
    while True:
        try:
            # Get some data from the socket and decode it
            message = socket.recv(65535)
            dec = message.decode()
            logging.debug("Recv < " + dec)
            if (dec == ""):
                return False

            # We might have gotten multiple motor commands, but we only care about the most recent one
            # The others can get thrown out; we can't update the motors fast enough to satisfy those commands
            lastjson = re.split("\r\n", dec)[-2]
            motor_dict = json.loads(lastjson)

            # Extract motor speeds from command and set motor to target that speed - they will try to get to that speed as fast as they can.
            # If another command comes in, the target speed might get updated faster than the speed can get actually set, but that's okay.
            # It's the client's responsibilty to set timers to ensure they don't overwhelm the robot
            speeds = [motor_dict["servos"][i]["servoSpeed"]
                      for i in range(len(motor_dict["servos"]))]
            motors.set_target_speed(speeds)

            await asyncio.sleep(0.05)
        except:
            await asyncio.sleep(0)


async def connection_handler(socket, sensors: Sensors, motors: Motors) -> None:
    # Asynchronously and concurrently handle incoming/outgoing messages with a single client
    await asyncio.gather(
        send(socket, sensors),
        listen(socket, motors)
    )


async def setup_server(sensors: Sensors, motors: Motors):
    # Start TCP Server that waits for VIPLE Wifi clients to connect to it
    global connection
    try:
        with socket.socket() as server_socket:
            host = get_ip()

            print("Starting Middleware Server on " + host + ":" + str(PORT))

            server_socket.bind((host, PORT))
            server_socket.listen(1)
            while True:
                # Accept a new connection
                logging.info("Waiting for connection...")
                conn, address = server_socket.accept()
                with conn:
                    conn.setblocking(0)
                    connection = conn

                    print()
                    logging.info(f"Successful connection with {str(address)}")

                    motors.headlights(True)
                    motors.set_servo_position(100)
                    await connection_handler(conn, sensors, motors)
                    # Stop the motors when the connection ends so the robot doesn't fly away
                    motors.set_target_speed((0, 0))
                    motors.headlights(False)

                    logging.info(f"End of connction with {str(address)}")
                    logging.info("--------------------------------------")
    except asyncio.CancelledError:
        logging.warning("Exiting connection.")


def main(argv):
    logging.basicConfig(level=logging.INFO)

    motors = Motors()
    stream = None
    with Camera() as cam:
        with ProcessedCamera(cam) as cam_proc:
            # Setup the sensor configuration
            sensors = create_ai_sensor_config(cam_proc)

            # Start up the video server so a client can remotely view the camera feed
            stream = Streamer(cam)

            # Start the server and start listening for connections on the main thread
            loop = asyncio.get_event_loop()
            try:
                main_task = asyncio.ensure_future(
                    setup_server(sensors, motors))
                loop.run_until_complete(main_task)
            except KeyboardInterrupt:
                print("Keyboard")
                loop.close()
                sentinel = True
            finally:
                logging.warning("Exiting middleware.")
                # Stop the motors when the
                motors.set_target_speed((0, 0))
                loop.close()
                stream.stop()
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
