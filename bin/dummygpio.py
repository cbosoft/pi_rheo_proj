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

def output(channel, value):
    pass
    
def input(channel):
    return 0
    
def setmode(numbering_system):
    pass
    
def setup(channel, direction):
    pass

def cleanup():
    pass

if __name__ == "__main__":
    print __doc__
