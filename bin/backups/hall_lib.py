#
# motor.py
#
# allows the accurate control of a motor's speed from a raspberry pi
#

# imports
import time
import thread as td
import RPi.GPIO as gpio
import sys

hall_pin = 16  # GPIO23

def incr(channel):
	global counter
	counter += 1

# set up pins
gpio.setmode(gpio.BOARD)
gpio.setup(hall_pin, gpio.IN, pull_up_down = gpio.PUD_UP)
counter = 0
gpio.add_event_detect(hall_pin, gpio.RISING, callback=incr)
time_period = 0.1
magnet_count = 2

try:
	while (True):
		sys.stdout.write('\r Speed (RPM):' + (str(float(counter * float(60 / (time_period * magnet_count)))) + ("").zfill(4))[:4])
		sys.stdout.flush()
		counter = 0
        	time.sleep(time_period)
except KeyboardInterrupt:
	gpio.cleanup()
