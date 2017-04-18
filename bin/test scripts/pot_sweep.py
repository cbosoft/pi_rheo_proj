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

mot = motor.motor(startnow=True, poll_logging=True, log_dir="./glyc_sweep_15ml", i_poll_rate=0.001)

print "Starting..."
mot.pot.set_resistance(48)
time.sleep(0.5)
try:
    for i in range(0, 127):
        print "Setting potval to {}, {}s to go.".format(i, ((127 - i) * 5))
        mot.pot.set_resistance(i)
        time.sleep(5)
    print "Done!"
    mot.clean_exit()
    
except KeyboardInterrupt:
    print "Interrupted!"
    mot.clean_exit()
