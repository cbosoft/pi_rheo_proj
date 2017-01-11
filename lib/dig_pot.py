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

    def set_reg(self, value):
        #set the value of the wiper register on the pot
        done = False
        while (not done):
            cur_val = self.read()
            if (value == cur_val):
                done = True
            elif (value > cur_val):
                self.decr()
            elif (value < cur_val):
                self.incr()

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

    def read(self):
        self.open()
        self.bus.write_byte_data(self.address + 1, 0, self.address + 1)
        byte = self.bus.read_i2c_block_data(self.address, 0, 2)
        self.close()
        return int((byte[0] << 8) + byte[1])

    def open(self):
        self.bus = SMBus(1)

    def close(self):
        self.bus.close()