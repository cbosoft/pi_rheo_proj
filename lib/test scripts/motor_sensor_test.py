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

mot = motlib.motor(max_speed=0, min_speed=0, sens_pin=16, trip_count=1, startnow=True, per_tick=True, per_span=True, log_dir="./params_check", input_logging=True, poll_logging=True)
mot.pot.set_resistance(32)
try:
    for j in range(0, 11):
        for i in range(0, 11):
            mot.i_poll_rate = float(i) * 0.02
            mot.span = float(j) * 0.1
            mot.new_logs(("IPR = {0:.3f} SPAN = {1:.3f} PV = 32").format(float(i) * 0.02, float(j) * 0.1))
            print (("IPR = {0:.3f} SPAN = {1:.3f} PV = 32").format(float(i) * 0.02, float(j) * 0.1))
            time.sleep(10)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
