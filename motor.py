#
# Motor class allows you to control a motor using adclib and daclib
#
import RPi.GPIO as GPIO
import adclib
import daclib

class Motor(object):
	cur_speed=0
	speed=0
	ADC = 0
	
	def __init__(self, ADC_):
		self.ADC = ADC_
	
	def set_speed(self, speed_):
		self.speed = speed_
		#not done, haven't decided how to control the motor's speed yet
		
	def get_speed(self):
		return self.ADC.get_real()
		
	def stop():
		self.set_speed(0)