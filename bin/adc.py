#
# adc.py
#
# Class library, gives support for using the MCP3008 8-channel 10bit ADC
#

import RPi.GPIO as gpio
import spidev as spi


class MCP3008(object):

    bus = 0  # holds the bus connection
    cs_pin = 0  # which GPIO pin is used to talk to this chip? (gpio.BOARD numbering) OR which cs channel to use
    vref = 3.3  # Reference voltage in use

    def __init__(self, cs_pin=1, vref=3.3):
        ''' 
        object = adc.MCP3008(**kwargs)
        
        Initialise MCP3008 ADC class object.
        
        kwargs:
        cs_pin - SPI chip select. Default is 1.
        vref - ADC reference voltage. Default is 3.3.
        '''
        
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
        
        channel - (int, 0-7) the ADC data channel that is to be read from.
        
        returns: (int, 0-1023) 10-bit value representing the voltage level on the channel specified.
        '''
        
        self.open()
        indat = self.bus.xfer2([1, 8 + channel << 4, 0])
        self.close()
        return ((indat[1] & 3) << 8) + indat[2]
        
    def read_volts(self, channel):
        '''
        read_volts(channel)
        
        Reads the voltage level on the specified channel.
        
        channel - (int, 0-7) the ADC data channel that is to be read from.
        
        returns float representing the voltage level on the channel specified.
        '''
        
        dat = self.read_data(channel)
        volts = (float(dat) / 1024.0) * self.vref
        return volts
        
    def write_byte(self, byte):
        '''
        write_byte(byte)
        
        byte - the 8 bit command to be sent to the ADC.
        '''
        
        self.open()
        command = [byte, 0]  # Two bytes; first is command shifted 4 bits, second is zero
        self.bus.writebytes(command)
        self.close()

    def open(self):
        '''
        open()
        
        opens a channel to the SPI device.
        
        Must completed by a following close() call.
        '''
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
        if (self.cs_pin > 1):
            gpio.output(self.cs_pin, gpio.LOW)
            self.bus.close()
        else:
            self.bus.close()
        
if __name__ == "__main__":
    # For debugging: 
    # reads and displays data from the ADC every time the enter key is pressed.
    # aconv = MCP3424()
    aconv = MCP3008()
    chan = 0
    # aconv.open_()
    try:
        while (True):
            print "\n\nValue: " + str(aconv.read_data(chan)) + "\n\n"
            print "Press enter to read another value, or ctrl-c to close."
            print "To change channel, enter the channel number and press enter."
            r = raw_input()

            if r == "1":
                chan = 1
            elif r == "0":
                chan = 0
        aconv.close()
    except KeyboardInterrupt:
        aconv.close()