import sys

sys.path.append("./..")

import motlib
import time

mot = motlib.motor(startnow=False, log_dir="./torq_get", i_poll_rate=0.001)

mot.pot.set_resistance(0)

r = raw_input("WHAT SPEED? ")
r = int(r)
if r < 0: r = 0
if r > 128: r = 128

mot.pot.set_resistance(r)

r = raw_input("PRESS ENTER TO BEEGIN)
mot.start_poll()

try:
    while True:
        print "LOGGING (0.5s)"
        time.sleep(0.5)
        mot.pause
        r = raw_input("PAUSED, WAITING.\n ENTER TO RESUME")
except KeyboardInterrupt:
    mot.pot.set_resistance(0)
    mot.clean_exit()


# End
mot.pot.set_resistance(0)
mot.clean_exit()
