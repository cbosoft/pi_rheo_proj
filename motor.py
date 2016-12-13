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
		#Provisionally using a DC:DC regulator with digital control via two momentary push switches jerry rigged to be pi-controllable via two optocouplers
		#Other programmable DC-DC regulators are being looked into, but few have the right specs for the 0-12v >1A operation required.
		
	def get_speed(self):
		return self.ADC.get_real()
		
	def stop():
		self.set_speed(0)