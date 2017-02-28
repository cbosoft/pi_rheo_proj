#
# Motor Speed Test Script
#
# Will set the digpot value and hold for some time before moving on to the next
#

import sys
sys.path.append('./..')

import motlib
import time

mot = motlib.motor(startnow=True, poll_logging=True, log_dir="./current_test_tues")

print "Starting..."
mot.pot.set_resistance(48)
time.sleep(0.5)
try:
    for i in range(0, 17):
        print "Setting potval to " + str(0 + (i * 8))
        mot.pot.set_resistance(0 + (i * 8))
        time.sleep(5)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
