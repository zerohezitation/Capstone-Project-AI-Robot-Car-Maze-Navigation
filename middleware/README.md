# Middleware

The Middleware is a Python program that has three main responsibilities:

1. Receive commands from the VIPLE client, decode them, and trigger the hardware (motors, headlights, and servos) to match those commands.
2. Collect updated sensor values (ultrasonic distance sensor, AI sensor, OpenCV sensor, etc.), and periodically send those values to the VIPLE client.
3. Optionally stream the robot's camera feed to a remote client.

## Installation

**Step 1.** Once the robot has been built according to the LABISTS manual, you must install Raspbian onto the microSD card in order to boot up the robot. See [here](https://www.raspberrypi.com/software/) for detailed instructions on Raspbian installation.

**Step 2.** Once you are booted up (and have connected a display, keyboard, and mouse), you now need to go to the Raspberry Pi Menu located in the top left and select `Preferences > Raspberry Pi Configuration > Interfaces`. Enable "I2C" and "Remote GPIO" if they are not already. Now would also be a good time to enable SSH and/or VNC server to be able to remote into the robot in the future, instead of needing to connect an HDMI cable, mouse, and keyboard.

**Step 3.** Next is dependency installation. For this step, you should connect the Raspberry Pi to the internet using a wired Ethernet cable or through a WiFi network. Python3 should come preinstalled with Raspbian, but we most also run the following commands:
```bash
pip install smbus2
pip install asyncio
pip install opencv-python
```
To use the `AiSensor` or `TrackOffsetSensor`, you must also install `tflite_runtime`.

If you plan on using VNC, run the following commands:
```bash
sudo apt-get update
sudo apt-get install realvnc-vnc-server
```

**Step 5.** We can now clone the middleware to the robot using the commands:
```bash
cd ~/Desktop # or another location
git clone https://github.com/zerohezitation/Capstone-Project-AI-Robot-Car-Maze-Navigation.git
```

**Step 4.** We need to configure the Raspberry Pi as an access point; that is, instead of using the wireless network interface to connect to a WiFi network, we have the Raspberry Pi broadcast an SSID that another computer can connect to as a WiFi network. This allows you to use the robot even if there is no network available.

There are multiple ways to set up the Raspberry Pi as an access point, but by far the easiest way is using the library [AutoAP](https://github.com/gitbls/autoAP). When setting up AutoAP, it will ask you for the name of the new SSID (such as "RaspberryPiRobot"), as well "Your WiFi SSID/Password"; **our recommendation is to not provide the latter, or provide fake values!** This will ensure the robot always goes into access point mode.

*Note: You cannot connect to a WiFi network and be in access point mode at the same time! This means that after you perform this step, you will not be able to download dependencies or anything else using WiFi. To connect to the internet without uninstalling AutoAP, you should connect a wired Ethernet cable.*

**Step 6.** To make the Middleware start up when the Raspberry Pi boots, we install a `systemd` service.
___

## Usage

**Step 1.** Turn on the robot. After ~1 minute, the Raspberry Pi should be booted up, gone into access point mode, and started up the middleware.

**Step 2.** On the machine running VIPLE, connect to the robot's WiFi network (i.e. "RPiRobot", with password "password123").

**Step 3.** Open your VIPLE program. Ensure that the "Robot Controller" block is set to "WiFi" mode, with the appropriate IP address (usually `192.168.16.1`) and port (usually `8124`).
If you are unsure about the IP address of the Raspberry Pi, open a command prompt and run `ipconfig`. The robot's IP address will be listed as your "default gateway".

**Step 4.** Run the VIPLE program (see the `viple` directory for example programs). A window should pop up saying "Running program". A further indication that the program is running is that the headlights will turn on while the program is running, and turn off when the program disconnects.

**Step 5. (optional)** You can view the robot's camera stream on a remote machine using `RemoteCamera` . Run the command `python3 -m common.remote_camera <robot IP address> --mode view` to see the raw video stream (see [common](../common/README.md) for details).

### Advanced Usage
You can start up the Middleware manually with the following command:
```bash
python3 -m middleware.main
```
You can optionally pass flag `-v` for verbose mode, `-p` to change the VIPLE port (default 8124), `--video_port` to change the Streamer port (default 8125), or `-i` to specify an interface other than "wlan0".

When the Middleware is running, the Streamer sever will also be started, but you can also run the video streamer standalone with the command:
```bash
python3 -m middleware.streamer
```
You can optionally pass `-p` to set the Streamer port (default is 8124), or `-i` to set an interface other than "wlan0"
___

## Troubleshooting

**I'm connected to the robot's WiFi network, but I get an error connecting to the robot when running my VIPLE program.** The Middleware is likely no longer running on the robot. Restart the robot to restart the Middleware, or remote into the robot using SSH/VNC and start the Middleware manually using the command:
```bash
python3 -m middleware.main
```
___