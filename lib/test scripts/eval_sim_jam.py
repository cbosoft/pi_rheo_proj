#
# Motor Speed Monitor Test Script
#
# Simulates the presence of a fluid shearing in the cell and occasionally spikes up a jamming occurence
#

import sys
sys.path.append('./..')

import motlib
import time

mot = motlib.motor(startnow=True, poll_logging=True, log_dir="./jam_test", i_poll_rate=0.001, log_note="jts=0.05")

jamming_time_scale = 0.05

try:
    print "Starting..."
    mot.pot.set_resistance(48)  # normal (base) speed
    time.sleep(0.5)
    for i in range(0, 20):
        print "Jamming!"
        mot.pot.set_resistance(24)
        time.sleep(jamming_time_scale)
        print "Un-jammed"
        mot.pot.set_resistance(48)
        time.sleep(10)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
