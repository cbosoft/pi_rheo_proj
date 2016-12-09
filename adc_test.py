# Imports
from time import sleep			# Import sleep method
from smbus2 import SMBus			# Import SMBus

bus = SMBus(1)				# Get I2C bus
ext_addr = 0x6e				# Set the ADC external address
int_addr = 220				# Set the ADC internal; address

# Setup
# Use channel 1 in continuous mode, with gain of 1 and 12bit data and 240 samples per second
# -> This is the default
# To set back to default, if has been changed, set the config reg as follows:
# bit: 76543210
# val: 10010000

# byte = 144				# (byte)144 = 10010000
# bus.write_byte(address, int_addr + 1)	# +1 signifies write operation
# bus.write_byte(address, byte)
# bus.close()

# Read voltage level in from ADC (voltage accross pot (0-3.3v)
# bus = SMBus(1)
bus.write_byte_data(ext_addr, 0, int_addr)
return_byte = bus.read_i2c_block_data(ext_addr, 0, 2)
print (return_byte[0] << 8) + return_byte[1]
bus.close()

# words
