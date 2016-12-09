#
# Class library, gives support for using the MCP3424 4-channel 16bit ADC
# Written by trial and error and extensive reading of the datasheet (see "MCP342xx.pdf")
# (Also great help from: https://www.youtube.com/watch?v=OPC5lXCKp_w)
#
# Imports
# from time import sleep			# Import sleep method
from smbus2 import SMBus			# Import SMBus


class mpc3424(object):
	bus = 0
	address = 0x6e
	channel = 0
	sample_rate = 0
	gain = 0
	
	def __init__(self, address_, channel_, sample_rate_, gain_):
		self.address = address_
		self.channel = channel_
		self.sample_rate = sample_rate_
		self.gain = gain_
		update_()
	
	def update_(self):
		open_()
		self.bus.write_byte_data(self.address, (self.channel << 5) + (1 << 4) + (self.sample_rate << 2) + (self.gain))
		close_()
		
	def send_byte(self, byte):
		open_()
		self.bus.write_byte_data(self.address, byte)
		close_()
		
	def read_data(self):
		open_()
		self.bus.write_byte_data(self.address, self.address)
		byte = self.bus.read_byte_data(self.address, 0, 2)
		close_()
		return byte
		
	def open_(self):
		self.bus = SMBus(1)
		
	def close_(self):
		self.bus.close()
