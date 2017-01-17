#
# motor.py
#
# allows the accurate control of a motor's speed from a raspberry pi
#

# imports
import time
import thread as td
import RPi.GPIO as gpio

hall_pin = 16  # GPIO23

def incr():
    global counter
    counter += 1

# set up pins
gpio.setmode(gpio.BOARD)
gpio.setup(hall_pin, gpio.IN, pull_up_down = gpio.PUD_UP)
counter = 0
gpio.add_event_detect(hall_pin, gpio.RISING, callback=incr)


try:
	while (True):
	        print "Speed:" + str(float(counter / 6)) 
            counter = 0
        	time.sleep(0.1)
except KeyboardInterrupt:
	gpio.cleanup()
