#
# dig_pot.py
#
# provides support for using an MCP4131 digital potentiometer with the raspberry pi using SPI

# imports
import spidev as spi
        
class MCP4131(object):
    '''
    SPI 10K Digital Potentiometer
    '''
    bus = 0  # holds the bus connection to the digital pot
    lav = 0
    chip_select = 0
    
    def __init__(self, chipselect=0):
        '''
        MCP4131()
        
        Creates an instance of the MCP4131 class for communicating over SPI with an MCP4131 digital potentiometer.
        
        kwargs:
        chipselect -  the chip_select address for the MCP4131 chip on the SPI network.
        '''
        self.bus = spi.SpiDev()
        self.chip_select = chipselect

    def set_resistance(self, value):
        '''
        set_resistance(value)
        Sets the value on the potentiometer.
        
        value - integer value to set on the potentiometer. The resistance betweeen the A terminal and the wiper will vary directly with this value.
        '''
        self.lav = value
        self.write_byte(value)
       
    def write_byte(self, byte):
        '''
        write_byte(byte)
        
        Writes the specified byte to the digital potentiometer.
        
        byte - the value to send to the potentiometer.
        '''
        self.open()
        command = [0, byte]
        self.bus.writebytes(command)
        self.close()

    def open(self):
        '''
        open()
        
        Begins communication with the potentiometer.
        Must be matched by an accompanying "close()"
        '''
        self.bus.open(0, self.chip_select)
        self.bus.max_speed_hz = 10000000

    def close(self):
        '''
        close()
        
        Ends communication with the potentiometer.
        '''
        self.bus.close()
