#
# Motor Speed Test Script
#
# Will set the digpot value and hold for a minute before moving on to the next - Small sweep from 48 to 128, step 8, hold 20s
#
import sys
sys.path.append('./..')

import motlib
import time
import matplotlib.pyplot as plt

hall_pin = 16
mag_count = 1
mot = motlib.motor(startnow=True, poll_logging=True, log_dir="./speed_test_new")

print "Starting..."
mot.pot.set_resistance(48)
time.sleep(2)
try:
    for i in range(0, 17):
        print "Setting potval to " + str(0 + (i * 8))
        mot.pot.set_resistance(0 + (i * 8))
        time.sleep(5)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
