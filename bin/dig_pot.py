'''
    Provides support for using an MCP4131 digital potentiometer with the Raspberry Pi over SPI
    
    Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# imports
import sys
try:
    import spidev as spi
except:
    debug = True
else:
    debug = False
        
class MCP4131(object):
    '''
    Usage:

    object = dig_pot.MCP4131()
    
    Creates an instance of the MCP4131 class for communicating over SPI with an MCP4131 digital potentiometer.
    
    **kwargs:
        chipselect      (integer)       The chip_select address for the MCP4131 chip on the SPI network.
    '''
    bus = 0  # holds the bus connection to the digital pot
    lav = 0
    chip_select = 0
    
    def __init__(self, chipselect=0):
        '''
        object = dig_pot.MCP4131()
        
        Creates an instance of the MCP4131 class for communicating over SPI with an MCP4131 digital potentiometer.
        
        **kwargs:
            chipselect      (integer)       The chip_select address for the MCP4131 chip on the SPI network.
        '''
        global debug
        if debug: return
        
        self.bus = spi.SpiDev()
        self.chip_select = chipselect

    def set_resistance(self, value):
        '''
        set_resistance(value)
        
        Sets the value on the potentiometer.
        
        Parameters:
            value           (integer)       Value to set on the potentiometer. The resistance betweeen the A 
                                            terminal and the wiper will vary directly with this value.
        '''
        global debug
        if debug: return
        
        self.lav = value
        self.write_byte(value)
       
    def write_byte(self, byte):
        '''
        write_byte(byte)
        
        Writes the specified byte to the digital potentiometer.
        
        Parameters:
            byte            (byte)          Value/command to send to the potentiometer.
        '''
        global debug
        if debug: return
        
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
        global debug
        if debug: return
        
        self.bus.open(0, self.chip_select)
        self.bus.max_speed_hz = 10000000

    def close(self):
        '''
        close()
        
        Ends communication with the potentiometer.
        '''
        global debug
        if debug: return
        
        self.bus.close()

if __name__ == "__main__":
    print __doc__
    print MCP4131.__doc__
