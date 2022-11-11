import socket
import asyncio
import json
import re
import sys
import logging
import argparse

from common.physical_camera import PhysicalCamera
from common.processed_camera import ProcessedCamera
from common.utils import get_ip
from middleware.devices.sensors.sensors import Sensors, create_ai_sensor_config
from middleware.devices.motors import Motors
from middleware.streamer import Streamer

# rate in milliseconds at which we send updated sensor values to client
SENSOR_POLLING_TIME = 500

sentinel = False


async def send(socket, sensors: Sensors) -> None:
    # Periodically update the server with new sensor values
    while not sentinel:
        try:
            #logging.debug("Getting updated sensor values")
            updated_values = sensors.read()
            #logging.debug("Dumping sensor output to JSON")
            json_response = json.dumps(updated_values)
            logging.info(f"Send > {json_response}")
            socket.send((json_response + "\r\n").encode())

            #logging.debug("Done sending message, going to sleep")
            await asyncio.sleep(SENSOR_POLLING_TIME / 1000)
            #logging.debug("Sender Done sleeping")
        except KeyboardInterrupt:
            break
        except BlockingIOError:
            await asyncio.sleep(0.1)
            continue
        except BrokenPipeError:
            break
        except OSError as e:
            logging.error("Error sending data.", e)
            break


async def listen(socket, motors: Motors) -> None:
    # Listen to all incoming messages from the server
    # Update the motors to match the speed we're sent
    while not sentinel:
        try:
            # Get some data from the socket and decode it
            #logging.debug("Receiving data from the socket")
            message = socket.recv(65535)
            #logging.debug("Decoding received message")
            dec = message.decode()
            logging.debug("Recv < " + dec)
            if (dec == ""):
                return False

            # We might have gotten multiple motor commands, but we only care about the most recent one
            # The others can get thrown out; we can't update the motors fast enough to satisfy those commands
            #logging.debug("Splitting received commands")
            commands = re.split("\r\n", dec)
            for command_json in commands:
                command = None
                try:
                    command = dict(json.loads(command_json))
                except json.decoder.JSONDecodeError:
                    continue
                logging.debug(f"Executing command: {command_json}")

                if ("servos" in command):
                    # Extract motor speeds from command and set motor to target that speed - they will try to get to that speed as fast as they can.
                    # If another command comes in, the target speed might get updated faster than the speed can get actually set, but that's okay.
                    # It's the client's responsibilty to set timers to ensure they don't overwhelm the robot
                    speeds = [command["servos"][i]["servoSpeed"]
                              for i in range(len(command["servos"]))]
                    motors.set_target_speed(speeds)
                if ("headlights" in command):
                    motors.headlights(command["headlights"])
                if ("camera_servo" in command):
                    motors.set_servo_position(command["camera_servo"])
        except KeyboardInterrupt:
            break
        except BlockingIOError:
            # If we're here, there weren't any messages in the socket when we called socket.recv()
            # Wait a little bit and listen for new messages
            await asyncio.sleep(0.1)
            continue
        except BrokenPipeError:
            break
        except OSError as e:
            logging.error("Error receiving data.", e)
            break

        # It is mandatory that the listener waits for some amount of time at the end of the iteration!
        # Otherwise the listener will never yield to the sender!
        logging.debug("Listener thread finished iteration, sleeping")
        await asyncio.sleep(0.05)
        logging.debug("Listener done sleeping")


async def connection_handler(socket, sensors: Sensors, motors: Motors) -> None:
    # Asynchronously and concurrently handle incoming/outgoing messages with a single client
    await asyncio.gather(
        send(socket, sensors),
        listen(socket, motors)
    )


async def setup_server(interface: str, port: int, sensors: Sensors, motors: Motors):
    global sentinel

    # Start TCP Server that waits for VIPLE Wifi clients to connect to it
    with socket.socket() as server_socket:
        host = get_ip(interface)

        print("Starting Middleware Server on " + host + ":" + str(port))

        server_socket.bind((host, port))
        server_socket.listen(1)

        # Set the timeout on the socket so that we don't get stuck on server_socket.accept()
        # Otherwise, we won't be able to properly close the socket when exiting
        server_socket.settimeout(0.5)

        while not sentinel:
            try:
                conn, address = server_socket.accept()

                # Make the connection non-blocking so that we don't get blocked waiting for IO in the listener
                conn.setblocking(False)

                with conn:
                    logging.info("--------------------------------------")
                    logging.info(
                        f"Successful connection with {str(address)}")

                    # Turn on the headlights and set the camera to the default position at the start of the program
                    motors.headlights(True)
                    motors.set_servo_position(100)

                    # Start listening for commands and sending sensor values until the connection ends
                    await connection_handler(conn, sensors, motors)

                    # Stop the motors when the connection ends so the robot doesn't fly away
                    motors.set_target_speed((0, 0))
                    motors.headlights(False)

                    logging.info(f"End of connction with {str(address)}")
                    logging.info("--------------------------------------")
            except KeyboardInterrupt:
                sentinel = True
                logging.debug("Shutting down socket...")
                server_socket.shutdown(socket.SHUT_RDWR)
                logging.debug("Finished shutting down socket.")
                break
            except socket.timeout:
                # If we're here, we timed out waiting for a VIPLE connection
                # Immediately start checking for new connections again
                # logging.debug(
                #    "Timed out waiting to connect to client, trying again...")
                continue
            except BlockingIOError as e:
                # Hopefully we don't get here, but it might happen if the middleware didn't
                # shut down properly before (i.e. the address/port is in use)
                logging.error("setup_server error", e)
                continue


def main(args: argparse.Namespace):
    global sentinel

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    # Start up the motors, headlights, servos, etc
    with Motors() as motors:
        # Start up the robot's physical camera
        with PhysicalCamera() as cam:
            # Start processing frames from the physical camera to create a virtual processed camera
            with ProcessedCamera(cam) as cam_proc:
                # Setup the sensor configuration
                with create_ai_sensor_config(cam_proc) as sensors:
                    # Start up the video server so a client can remotely view the camera feed
                    with Streamer(cam, args.interface, args.video_port) as stream:
                        # Start the server and start listening for connections on the main thread
                        loop = asyncio.get_event_loop()
                        try:
                            main_task = asyncio.ensure_future(
                                setup_server(args.interface, args.port, sensors, motors))
                            loop.run_until_complete(main_task)
                        except KeyboardInterrupt:
                            sentinel = True
                        finally:
                            logging.info("Exiting middleware.")
                            loop.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python3 -m middleware.main",
        description="Middleware for Raspberry Pi Robot.",
    )
    parser.add_argument("-v", "--verbose",
                        help="Enable verbose logging output", action="store_true", dest="verbose")
    parser.add_argument("-p", "--port", type=int,
                        help="the VIPLE connection port (usually 8124)", default=8124, dest="port")
    parser.add_argument("--video_port", type=int,
                        help="the robot video streaming server port (usually 8125)", default=8125, dest="video_port")
    parser.add_argument(
        "-i", "--interface", help="the name of the network interface to host the connection on (usually 'wlan0' for the Raspberry Pi wireless interface)", default="wlan0", dest="interface")

    args = parser.parse_args()

    main(args)
