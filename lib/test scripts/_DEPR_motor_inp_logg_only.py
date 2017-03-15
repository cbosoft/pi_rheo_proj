#
# Motor Interval Test Script
#
# Will set the digpot value and hold for a minute before moving on to the next, only logging the sensor input
#
import sys
sys.path.append('./..')

import motlib
import time
import matplotlib.pyplot as plt

hall_pin = 16
mag_count = 1
mot = motlib.motor(sens_pin=16, trip_count=1, startnow=False, poll_logging=False, input_logging=True, log_note="input logging only",  per_tick=False, per_span=False, log_dir="./inp_only")

print "Starting..."
mot.pot.set_resistance(0)
mot.span = 0.5
time.sleep(2)
try:
    for i in range(0, 9):
        mot.new_logs("PV = " + str(i * 16))
        print "Setting potval to " + str((i * 16))
        mot.pot.set_resistance((i * 16))
        time.sleep(10)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
