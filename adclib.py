#
# Class library, gives support for using the MCP3424 4-channel 16bit ADC
# Written by trial and error and extensive reading of the datasheet (see "MCP342xx.pdf")
# (Also great help from: https://www.youtube.com/watch?v=OPC5lXCKp_w)
#

from smbus2 import SMBus


class mpc3424(object):
	bus = 0									#holds the bus connection
	address = 0x6e								#address of the adc (in hex, set by setting pins on 
										#the adc high or low
	channel = 0								#(0-3) four different analogue inputs
	sample_rate = 0								#(0-3) sets sample rate
										#higher sample rate, lower resolution
	gain = 0								#(0-3) for small voltages (<<VDD) use gain to increase resolution
										#voltage gain = 2^gain => gain=2: x4
	
	def __init__(self, address_, channel_, sample_rate_, gain_):
		self.address = address_						#set the local variable values (software params)
		self.channel = channel_
		self.sample_rate = sample_rate_
		self.gain = gain_						
		self.update_()							#sync params between software and adc
	
	def update_(self):
		self.open_()							#open bus connections
		self.bus.write_byte_data(self.address, 0, (self.channel << 5) + (1 << 4) + (self.sample_rate << 2) + (self.gain))
										#set the parameters on the adc
		self.close_()							#close bus connection
		
	def write_byte(self, byte):						#NOT USED! WHY IS IT HERE?
		self.open_()							#open bus connection
		self.bus.write_byte_data(self.address, 0, byte)			#write specified byte data to adc
		self.close_()							#close bus connection
		
	def read_data(self):
		self.open_()							#open bus connection
		self.bus.write_byte_data(self.address, 0, self.address)		#tell adc to expect the spanish inquisition
		b = self.output_bits()
		if (b == 18):
			b = 3							#3 bytes to hold 18 bits
		else:
			b = 2							#2bytes to hold 12 to 16 bits
		byte = self.bus.read_i2c_block_data(self.address, 0, b)
		self.close_()							#close the connection
		total = 0
		for i in range(0, b):
			total += (byte[i] << ((b - i - 1) * 8))			#getting total
		return total
		
	def output_bits(self):
		if (self.sample_rate == 0):
			return 12						#240 samples per second (SPS)
		elif (self.sample_rate == 1):
			return 14						#60 SPS
		elif (self.sample_rate == 2):
			return 16						#15 SPS
		elif (self.sample_rate == 3):
			return 18						#3.75 SPS
		else:
			self.sample_rate = 0					#sample rate wasn't set correctly, reset to default (0)
			self.update_()
		
	def open_(self):
		self.bus = SMBus(1)						#get bus
		
	def close_(self):
		self.bus.close()						#close bus
