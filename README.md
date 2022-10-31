# Capstone-Project-AI-Robot-Car-Maze-Navigation

## Middleware User Manual:
### Setting up a new car
#### Step 1
Try booting up the Raspberry Pi using the Labists SD card that comes with the car or follow the note below if you coose to use a different SD card.
##### **Note: If the Raspberry Pi is unable to boot due too not having Raspian installed then you need to use the flash drive with the SD card inserted and download Raspian onto the SD card.**

#### Step 2
After downloading Raspian, try booting the Raspberry Pi up once again. If it is unable to boot up then re-install Raspian and try again.
When going through the setup you will need to connect to a Wi-Fi network, or connect to one once you make it to the Desktop screen.
##### **Note: Make sure you have the HDMI connected to 2nd HDMI port sometimes it wont boot up if it is connect to the port closest to the power port.**

#### Step 3 
Once you are booted up now you need to go to the Raspberry Pi Menu located in the top left and then
select Prefrences > Raspberry Pi Configuration > Interfaces and make sure that I2C and Remote GPIO are enabled.
##### **Helpful: To make life easier we also suggest enabling VNC so that you can connect from a desktop or laptop to the Raspberry Pi without having to connect your keyboard and mouse to the Raspberry PI.**

#### Step 4 
Now make a new terminal window and install the following dependencies which are used in the middleware by using these commands:
###### pip install websockets
###### pip install smbus2
###### pip install asyncio

Commands to run to use VNC:
###### sudo apt-get update
###### sudo apt-get install realvnc-vnc-server

#### Step 5
Now retrieve the middleware files located in GitHub repository and store them somewhere easy to access on the Raspberry Pi.

### Using the Middleware
#### Step 1 - Connect to the Robot
Upon plugging in the robot to power (via the back USB port and turning the switch on), the Raspberry Pi will start to boot up. Once booted up, the Pi will automatically enter access point mode. On your client machine, you will see a wireless network named "RPiRobotX", which you can connect to with the default password "password123".

#### Step 2 - Start the Middleware
Ideally, this step should be completed automatically. Installed on the Raspberry Pi is a service that automatically starts the middleware up on boot. To start the middleware manually, you will need to remotely control the Raspberry Pi using VNC or SSH. Navigate to the directory containing the middleware, and run:
```./start_middleware.sh```
You should see the following output in the console if successful:

#### Step 3 - Start your VIPLE Program
Once the middleware is started up, you can start to control the robot using a VIPLE program. Ensure the controller is configured with the IP address of the Raspberry Pi, which should be statically assigned to IP `192.168.16.1`. The middleware runs on port `8124` by default.

Click the triangle to start running the VIPLE program:

When the program is executing, and the connection is successfully established, the headlights on the car will turn on, and they will turn off when the connection ends.

Note: Sometimes if the connection fails, or execution stops prematurely, the robot will continue in motion. To immediately stop the motors without turning off the Pi, press the small switch in the bottom-left corner of the daughter board.

#### Step 4 (optional)
start the video streaming client
if you'd like to view the video stream of the robot, you can connect to the video server using the provided RemoteCamera class.
run: python3 -m common.camera 192.168.16.1
on the machine connected to the raspberry pi