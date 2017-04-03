#
# Motor Speed Test Script
#
# Will set the digpot value and hold for some time before moving on to the next
#

import sys
sys.path.append('./..')

import motor
import time

mot = motor.motor(startnow=True, poll_logging=True, log_dir="./filter_test", i_poll_rate=0.001, filtering="butter")

print "Starting..."
mot.pot.set_resistance(48)
time.sleep(0.5)
try:
    for i in range(0, 128):
        print "Setting potval to " + str(0 + (i))
        mot.pot.set_resistance(0 + (i))
        time.sleep(2)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
