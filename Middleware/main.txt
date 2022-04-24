import websockets
import asyncio
import json
import re
import threading
import time
from sensor import get_distance
import testmotor

HOST = "10.3.44.16"
PORT = 8124

LEFT_WHEEL_PORT = 3
RIGHT_WHEEL_PORT = 5

SENSOR_POLLING_TIME = 100 # polling rate in milliseconds

sensors_dict = {
    "sensors": [{
        "name": "distance",
        "id": 1,
        "value": 50
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
        json_response = json.dumps(sensors_dict)
        print("Send > " + json_response)
        await websocket.send(json_response)
        await asyncio.sleep(SENSOR_POLLING_TIME / 1000)

# Listen to all incoming messages from the server
async def listen(websocket):
    global motor_dict
    async for message in websocket:
        print(message)
        print("Recv < " + message)
        motor_dict = json.loads(message)
        print(motor_dict)
        

# Asynchronously and concurrently handle incoming/outgoing messages
async def handler(websocket):
    await asyncio.gather(
        send(websocket),
        listen(websocket),
    )

# Open the connection with the server via a websocket
# Start listening to messages sent from server, and periodically send sensor values back to server
async def setup_connection():
    print(f"Opening websocket connection with \'{HOST}:{PORT}\'...")
    async with websockets.connect(f"ws://{HOST}:{PORT}") as websocket:
        print(f"Successfully connected to \'{HOST}:{PORT}\'.")
        await handler(websocket)

# TODO spawn a new thread that updates the sensor values
def update_sensors():
    while True:
        time.sleep(0.5)
        # get updated sensor data
        distance = get_distance()
        sensors_dict["sensors"][0]["value"]= distance

# TODO spawn a new thread that updates the motor power values based on messages from the server
def update_motors():
    while True:
        #print(motor_dict["servos"][0]["servoSpeed"])
        #print(motor_dict)
        if(motor_dict["servos"][0]["servoSpeed"] > 0 and motor_dict["servos"][1]["servoSpeed"] > 0) :
            testmotor.go_Forward()
        elif(motor_dict["servos"][0]["servoSpeed"] < 0 and motor_dict["servos"][1]["servoSpeed"] < 0) :
            testmotor.go_Backward()
        elif(motor_dict["servos"][0]["servoSpeed"] < 0 and motor_dict["servos"][1]["servoSpeed"] > 0) :
            testmotor.go_Left()
        elif(motor_dict["servos"][0]["servoSpeed"] > 0 and motor_dict["servos"][1]["servoSpeed"] < 0) :
            testmotor.go_Right()
        elif(motor_dict["servos"][0]["servoSpeed"] == 0 and motor_dict["servos"][1]["servoSpeed"] == 0) :
            testmotor.stop()

# Main loop
def main():
    t1 = threading.Thread(target=update_sensors, args=[])
    t1.start()
    t2 = threading.Thread(target=update_motors, args=[])
    t2.start()
    
    try:
        # open the websocket connection to start sending/receiving from the server
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(setup_connection())
        loop.run_forever()
    finally:
        print("Closing connection.")

if __name__ == "__main__":
    main()
