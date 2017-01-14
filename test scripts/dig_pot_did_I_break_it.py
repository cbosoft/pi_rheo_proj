# digi pot test
# did i melt it when soldering? :S

from smbus2 import SMBus

# read TCON reg
print "Creating bus connection"
bus = SMBus(1)

print "Asking for TCON data"
bus.write_byte_data(0x5C,0,76)

print "Recieving TCON data"
byte = bus.read_i2c_block_data(0x5C,0, 2)

print "Closing bus connection"
bus.close()

print "Data recieved:"
print bin((byte[0] << 8) + byte[1])