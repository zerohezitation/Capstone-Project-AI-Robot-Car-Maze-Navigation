# Capstone-Project-AI-Robot-Car-Maze-Navigation

## Middleware User Manual:
### Setting up a new car
#### Step 1
Try booting up the Raspberry Pi using the Labists SD card that comes with the car or follow the note below if you coose to use a different SD card.
###### **Note: If the Raspberry Pi is unable to boot due too not having Raspian installed then you need to use the flash drive with the SD card inserted and download Raspian onto the SD card.**

#### Step 2
After downloading Raspian, try booting the Raspberry Pi up once again. If it is unable to boot up then re-install Raspian and try again.
When going through the setup you will need to connect to a Wi-Fi network, or connect to one once you make it to the Desktop screen.
###### **Note: Make sure you have the HDMI connected to 2nd HDMI port sometimes it wont boot up if it is connect to the port closest to the power port.**

#### Step 3 
Once you are booted up now you need to go to the Raspberry Pi Menu located in the top left and then
select Prefrences > Raspberry Pi Configuration > Interfaces and make sure that I2C and Remote GPIO are enabled.
###### **Helpful: To make life easier we also suggest enabling VNC so that you can connect from a desktop or laptop to the Raspberry Pi 
without having to connect your keyboard and mouse to the Raspberry PI.**

#### Step 4 
Now make a new terminal window and install the following dependencies which are used in the middleware by using these commands:
pip install websockets
pip install smbus2
pip install asyncio

Commands to run to use VNC:
sudo apt-get update
sudo apt-get install realvnc-vnc-server

#### Step 5
Now retrieve the middleware files located in GitHub repository and store them somewhere easy to access on the Raspberry Pi.

### Using the Middleware
#### Step 1
Ensure that you are connected to a Wi-Fi network and your ASU VIPLE program is also running on the same network. 
Open a new terminal and type the command 'ifconfig' you will need to save the host ip address for that network and either modify the 'main.py' file with the 
new address or pass it in as an argument when you run the program which will be explained in Step 2.

#### Step 2
Open a new terminal and go to the directory where you have the middle ware files stored.
Before executing the program make sure that your VIPLE program is running on another computer.
To run the middleware use the command:
python main.py
###### **Note: The above command will work if you modified the 'main.py' file with the new host ip address from the Wi-Fi network you are connected to.**
To run the middleware by passing the host ip address through the command line use the command:
python main.py -h *insert host ip address*
###### **Note: If you are using a specific port other than '8124' on your VIPLE program then you can also pass that as an argument as well**
To run the middleware by passing in both the host ip address and port through the command line use the command:
python main.py -h *insert host ip address* -p *insert port*

#### Step 3
The program should connect to the host and port. Once connected, the program will start to return distance values in JSON as output in the terminal.
Now you can test your VIPLE program.
  
