#
# Voltage regulator jerry rig
#

import RPi.GPIO as GPIO
from time import sleep

class v_reg(object):
	
	up_pin = 0
	down_pin = 0
	
	def __init__(self, up_pin_, down_pin_)
		GPIO.setmode(GPIO.BCM)
		self.up_pin = up_pin_
		self.down_pin = down_pin_
		GPIO.setup(self.up_pin, GPIO.OUT)
		GPIO.setup(self.down_pin, GPIO.OUT)
		
	def increase(self, steps=1)
		for i in range(0, steps):
			GPIO.output(self.up_pin, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(self.up_pin, GPIO.LOW)
			sleep(0.01)
		
	def decrease(self, steps=1)
		for i in range(0, steps):
			GPIO.output(self.down_pin, GPIO.HIGH)
			sleep(0.01)
			GPIO.output(self.down_pin, GPIO.LOW)
			sleep(0.01)
		
	def end(self):
		GPIO.cleanup()