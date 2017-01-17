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

# set up pins
gpio.setmode(gpio.BOARD)
gpio.setup(hall_pin, gpio.IN, pull_up_down = gpio.PUD_UP)

try:
	while (True):
	        print str(gpio.input(hall_pin)) 
        	time.sleep(0.5)
except KeyboardInterrupt:
	gpio.cleanup()
