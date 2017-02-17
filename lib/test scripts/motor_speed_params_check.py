#
# Motor Speed Test Script
#
# Will sweep through the different parameters available to the speed sensor algorithm to determine which set up to use
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
mot.per_tick = True
mot.per_span = True
mot.log_dir = "./dat+plot/paramscheck"

time.sleep(2)
try:
    mot.pot.set_resistance(64)
    for i in range(1, 11):
        for j in range(1, 11):
            mot.log_note = "Span = " + str(float(i) / 10.0) + ", Tick = " + str(float(j) / 20.0)
            print "Span = " + str(float(i) / 10.0) + ", Tick = " + str(float(j) / float(20))
            mot.new_logs()
            mot.span = float(i) / float(10)
            mot.tick = float(j) / float(20)
            time.sleep(10)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
