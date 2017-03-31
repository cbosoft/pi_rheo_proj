#
# Motor Speed Test Script
#
# Will set the digpot value and hold for some time before moving on to the next
#
# To eliminate aliasing in recording, the data will be recorded with different poll rates (0.001, 0.01, and 0.1)
#

import sys
sys.path.append('./..')

import motor
import time

mot = motor.motor(startnow=True, poll_logging=True, log_dir="./long_sweep", i_poll_rate=0.001)

print "Starting..."
mot.pot.set_resistance(48)
time.sleep(0.5)
try:
    for j in range(0, 2):
        for i in range(0, 127):
            print "Setting potval to " + str(i)
            mot.pot.set_resistance(i)
            time.sleep(5)
        mot.i_poll_rate= mot.i_poll_rate * 10
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
