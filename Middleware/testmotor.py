import time
from smbus2 import SMBus

# Initialize

# Use /dev/i2c1
I2C_BUS = SMBus(1)
time.sleep(1)

I2C_ADDRESS = 0x18
I2C_COMMAND = 0xff

# Motor
I2C_STOP     = 0x210A
I2C_FORWARD  = 0x220A
I2C_BACKWARD = 0x230A
I2C_LEFT     = 0x240A
I2C_RIGHT    = 0x250A

I2C_LEFT_SPEED_SLOW  = 0x2605
I2C_LEFT_SPEED_FAST  = 0x260A
I2C_RIGHT_SPEED_SLOW = 0x2705
I2C_RIGHT_SPEED_FAST = 0x270A


I2C_HEADLIGHT_LEFT_OFF  = 0x3600
I2C_HEADLIGHT_LEFT_ON   = 0x3601
I2C_HEADLIGHT_RIGHT_OFF = 0x3700
I2C_HEADLIGHT_RIGHT_ON  = 0x3701

def go_Forward():

    I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_FORWARD)

def go_Backward():
    I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_BACKWARD)
    
def go_Left():
    #I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_LEFT_SPEED_SLOW)
    I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_LEFT)

def go_Right():
    #I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_RIGHT_SPEED_FAST)
    I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_RIGHT)

def stop():
    I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_STOP)

#def turn_circle():
# I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_LEFT_SPEED_FAST)
# time.sleep(0.01)
# I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_RIGHT_SPEED_FAST)
# time.sleep(0.01)
# I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_LEFT)
# time.sleep(2)
# I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_RIGHT)
# time.sleep(2)
# I2C_BUS.write_word_data(I2C_ADDRESS, I2C_COMMAND, I2C_STOP)
# time.sleep(0.01)

