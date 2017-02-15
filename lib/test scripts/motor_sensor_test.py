#
# Motor Speed Test Script
#
# Will set the digpot value and hold for a while before increasing the pot value
#
import sys
sys.path.append('./..')

import motlib
import time
import matplotlib.pyplot as plt

hall_pin = 16
mag_count = 1
mot = motlib.motor(0, 0, hall_pin, mag_count, startnow=True, per_tick=True, per_span=True, log_dir=r"./interval testing/" + time.strftime("%H:%M:%S", time.gmtime() + "/")

try:
    for i in range(0, 8):
        print "Setting potval to " + str((i * 16))
        mot.pot.set_resistance((i * 16))
        time.sleep(10)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
