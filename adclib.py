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
		self.update_()
	
	def update_(self):
		self.open_()
		self.bus.write_byte_data(self.address, (self.channel << 5) + (1 << 4) + (self.sample_rate << 2) + (self.gain))
		self.close_()
		
	def send_byte(self, byte):
		self.open_()
		self.bus.write_byte_data(self.address, byte)
		self.close_()
		
	def read_data(self):
		self.open_()
		self.bus.write_byte_data(self.address, self.address)
		b = self.output_bits()
		if (b == 18):
			b = 3
		else:
			b = 2
		byte = self.bus.read_i2c_block_data(self.address, 0, b)
		self.close_()
		total = 0
		for i in range(0, b - 1):
			total += (byte[i] << ((b - i) * 8))
		return total
		
	def output_bits(self):
		if (self.sample_rate == 0):
			#is 240 samples per second
			return 12
		elif (self.sample_rate == 1):
			#60 SPS
			return 14
		elif (self.sample_rate == 2):
			#15 SPS
			return 16
		elif (self.sample_rate == 3):
			#3.75 SPS
			return 18
		else:
			return 0
		
	def open_(self):
		self.bus = SMBus(1)
		
	def close_(self):
		self.bus.close()
