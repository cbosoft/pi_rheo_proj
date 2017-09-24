#
# dummygpio.py
#
# dummy gpio class
# for debugging

'''
    Pretends to be the GPIO package if program is not run on a Raspberry Pi.
    
    Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

HIGH = True
LOW = False

OUT = 1
IN = 0

BCM = 0
BOARD = 0

PUD_UP = 0
PUD_DOWN = 1

RISING = 0
FALLING = 1
BOTH = 2

def output(channel, value):
    pass
    
def input(channel):
    return 0

class PWM(object):
    def __init__(self, channel, frequency):
        self.channel = channel
        self.frequency = frequency
        self.dc = 0.5
    
    def start(self, dc):
        self.dc = dc
    
    def stop(self):
        pass
    
    def ChangeDutyCycle(self, dc):
        self.dc = dc
    
    def ChangeFrequency(self, frequency):
        self.frequency = frequency
    
def setmode(numbering_system):
    pass
    
def setup(channel, direction, pull_up_down=0):
    pass

def add_event_detect(pin, direction, callback=None):
    pass

def setwarnings(b):
    pass

def cleanup():
    pass

if __name__ == "__main__":
    print __doc__
