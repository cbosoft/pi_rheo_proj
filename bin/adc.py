'''
    Provides class object for handling an MCP3008 ADC from a Raspberry Pi over SPI.

    Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# System
import sys

# 3rd Party
try:
    import RPi.GPIO as gpio
    import spidev as spi
except:
    debug = True
else:
    debug = False


class MCP3008(object):
    ''' 
    Usage:

    object = adc.MCP3008(**kwargs)

    Initialise MCP3008 ADC class object.

    **kwargs:
        cs_pin      (integer)       SPI chip select. Default is 1
        vref        (float)         ADC reference voltage. Default is 3.3
    '''

    bus = 0  # holds the bus connection
    cs_pin = 0  # which GPIO pin is used to talk to this chip? (gpio.BOARD numbering) OR which cs channel to use
    vref = 3.3  # Reference voltage in use

    def __init__(self, cs_pin=1, vref=3.3):
        ''' 
        object = adc.MCP3008(**kwargs)
        
        Initialise MCP3008 ADC class object.
        
        **kwargs:
            cs_pin      (integer)       SPI chip select. Default is 1
            vref        (float)         ADC reference voltage. Default is 3.3
        '''
        global debug
        if debug: return
        
        # Chip select setup
        self.cs_pin = cs_pin
        if (cs_pin > 1):  # using the GPIO pins as chip_select pins
            gpio.setmode(gpio.BOARD)
            gpio.setup(self.cs_pin, gpio.OUT, pull_up_down=gpio.PUD_UP)  # chip select is normally high, pulled up by the RPi, just like any gpio, its not electrically low
            gpio.output(self.cs_pin, gpio.HIGH)
        else:  # using the Pi's built in chip select method
            pass
        
        # Set up bus connection
        self.bus = spi.SpiDev()
        
        # Vref setting
        self.vref = vref
        
    def read_data(self, channel):
        '''
        read_data(channel)
        
        Converts the voltage (relative to vref) on the specified channel to a 10-bit number.
        
        Parameters:
            channel     (integer)       The ADC data channel that is to be read from. Must be in
                                        range of 0 to 7 inclusive.
        
        Returns: 
            data        (integer)       10-bit value representing the voltage level on the channel specified.
        '''
        global debug
        if debug: return
        
        self.open()
        indat = self.bus.xfer2([1, 8 + channel << 4, 0])
        self.close()
        return ((indat[1] & 3) << 8) + indat[2]
        
    def read_volts(self, channel):
        '''
        read_volts(channel)
        
        Reads the voltage level on the specified channel.
        
        Parameters:
            channel     (integer)       The ADC data channel that is to be read from. Must be in
                                        range of 0 to 7 inclusive.
        
        Returns:
            volts       (float)         The voltage level on the channel specified.
        '''
        global debug
        if debug: return
        
        dat = self.read_data(channel)
        volts = (float(dat) / 1024.0) * self.vref
        return volts
        
    def write_byte(self, byte):
        '''
        write_byte(byte)
        
        Writes a byte of information to the ADC.
        
        Parameters:
            byte        (byte)          The 8 bit command to be sent to the ADC.
        '''
        global debug
        if debug: return
        
        self.open()
        command = [byte, 0]  # Two bytes; first is command shifted 4 bits, second is zero
        self.bus.writebytes(command)
        self.close()

    def open(self):
        '''
        open()
        
        Opens a channel to the SPI device.
        
        Must completed by a following close() call.
        '''
        global debug
        if debug: return
        
        if (self.cs_pin > 1):
            gpio.output(self.cs_pin, gpio.HIGH)
            self.bus.open(0, 1)
            self.bus.max_speed_hz = 10000000
        else:
            self.bus.open(0, self.cs_pin)
            self.bus.max_speed_hz = 10000000

    def close(self):
        '''
        close()
        
        closes a (previously opened) channel to the SPI device.
        '''
        global debug
        if debug: return
        
        if (self.cs_pin > 1):
            gpio.output(self.cs_pin, gpio.LOW)
            self.bus.close()
        else:
            self.bus.close()
        
if __name__ == "__main__":
    print __doc__
    print MCP3008.__doc__
