#
# dig_pot.py
#
# provides support for using an MCP4531 digital potentiometer with the raspberry pi over I2C

# imports
from smbus2 import SMBus


class MCP4531(object):

    bus = 0  # holds the bus connection to the digital pot (empty when not in use)

    address = 0x5C  # 01011100

    def __init__(self, addr=0x5C):
        self.address = addr
        self.reg_setup()

    def set_resistance(self, value):
        # set the value of the wiper register on the pot
        
        # the command takes the form (MSB to LSB):
        # register address (4 bits)
        # write/increment/decrement/read (2 bits)
        # unused (1 bit)
        # data to write (9 bits)
        
        # note: the data is 9bit, but the pot is only 7bit.
        
        # command = [int("00000000", 2), value]
        command = [0, value]
        self.write_bytes(command)

    def reg_setup(self):
        # sets up the terminal control (TCON) register on the potentiometer
        
        # the command consists of two bytes:
        # the first (most significant) 6bits of the first byte are the command itself, 
        # telling the pot that we want to talk to the TCON register
        # write mode is set by the last digit on the address byte ("0")
        # the next bit is ignored
        # the final bit in the first byte is the most significant bit of the data to write
        
        # The TCON register:
        # bit 8     General call enabled?
        # bit 7     not used on this device
        # bit 6     not used on this device
        # bit 5     not used on this device
        # bit 4     not used on this device
        # bit 3     not sure
        # bit 2     terminal A connected?
        # bit 1     wiper connected?
        # bit 0     terminal B connected?
        
        command = [int("01000010", 2), int("00000111", 2)]
        self.write_bytes(command)
        
    def incr(self):
        incr_command = 0x84
        self.write_byte(incr_command)

    def decr(self):
        decr_command = 0x88
        self.write_byte(decr_command)

    def write_byte(self, byte):
        self.open()
        self.bus.write_byte_data(self.address, 0, byte)
        self.close()
       
    def write_bytes(self, bytes):
        self.open()
        self.bus.write_i2c_block_data(self.address, 0, bytes)
        self.close()

    def read(self):
        self.open()
        self.bus.write_byte_data(self.address + 1, 0, int("00001100", 2))
        byte = self.bus.read_i2c_block_data(self.address, 0, 2)
        self.close()
        return int((byte[0] << 8) + byte[1])

    def open(self):
        self.bus = SMBus(1)

    def close(self):
        self.bus.close()