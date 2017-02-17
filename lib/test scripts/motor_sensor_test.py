#
# Motor Speed Test Script
#
# Will set the digpot value and hold for a while before increasing
#
import sys
sys.path.append('./..')

import motlib
import time
import matplotlib.pyplot as plt

mot = motlib.motor(max_speed=0, min_speed=0, sens_pin=16, trip_count=1, startnow=True, per_tick=True, per_span=True, log_dir="./interval_testing/" + time.strftime("%d %m %Y - %H %M %S", time.gmtime()), input_logging=True, poll_logging=True)

try:
    for i in range(0, 8):
        print "Setting potval to " + str((i * 16))
        mot.pot.set_resistance((i * 16))
        time.sleep(10)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
