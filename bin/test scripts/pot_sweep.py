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

mot = motor.motor(startnow=True, poll_logging=True, log_dir="./g0_vary", i_poll_rate=0.001)

print "Starting..."
mot.pot.set_resistance(48)
time.sleep(0.5)
interval = 16 # in s
step = 8
try:
    for i in range(0, (128 / step) + 1):
        print "Setting potval to {}, {}s to go.".format((i * step), (((128 / step) - i + 1) * interval))
        mot.pot.set_resistance((i * step))
        time.sleep(interval)
    print "Done!"
    mot.clean_exit()
    
except KeyboardInterrupt:
    print "Interrupted!"
    mot.clean_exit()
