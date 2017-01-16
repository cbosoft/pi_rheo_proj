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
gpio.setmode(GPIO.BOARD)
gpio.setup(hall_pin, GPIO.IN)

try:
	while (True):
        print str(GPIO.input(hall_pin))
        time.sleep(0.5)
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		gpio.cleanup()