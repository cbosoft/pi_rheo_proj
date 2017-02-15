#
# Motor Speed Test Script
#
# Will set the digpot value and hold for a minute before moving on to the next
#
import sys
sys.path.append('./..')

import motlib
import time
import matplotlib.pyplot as plt

hall_pin = 16
mag_count = 1
mot = motlib.motor(0, 0, hall_pin, mag_count, True)

print "Starting..."
mot.pot.set_resistance(0)
mot.per_tick = False
mot.span = 0.5
mot.log_dir = "./"
time.sleep(2)
try:
    for i in range(0, 7):
        print "Setting potval to " + str((i * 16))
        mot.pot.set_resistance((i * 16))
        time.sleep(10)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
