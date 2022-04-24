import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

ECHO = 5
TRIG = 6

GPIO.setwarnings(False)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

def get_distance():


    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    while GPIO.input(ECHO) == False:
        start = time.time()

    while GPIO.input(ECHO) == True:
        end = time.time()

    sig_time = end-start

    #CM:
    distance = sig_time / 0.000058
    
    #round(distance,2)

    #inches:
    #distance = sig_time / 0.000148
    #print('Distance: {:0.2f} centimeters'.format(distance))

    return distance

#while True:
#     distance = get_distance()
#     time.sleep(1)
    
