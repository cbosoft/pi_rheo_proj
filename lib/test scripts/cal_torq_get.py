import sys

sys.path.append("./..")

import motlib
import time

mot = motlib.motor(startnow=False, log_dir="./torq_get", i_poll_rate=0.001, filtering="gaussian")

mot.pot.set_resistance(0)

r = raw_input("WHAT SPEED? ")
r = int(r)
if r < 0: r = 0
if r > 128: r = 128

mot.pot.set_resistance(r)

r = raw_input("PRESS ENTER TO BEEGIN")
mot.start_poll()

try:
    while True:
        print "LOGGING (0.5s)"
        time.sleep(0.5)
        mot.log_pause()
        r = raw_input("PAUSED, WAITING.\n ENTER TO RESUME\n ANY TEXT IS RESUME NOTE")
        if r == "": r = "resumed: {0}".format(time.strftime("%X", time.gmtime()))
        mot.log_resume(r)
except KeyboardInterrupt:
    mot.pot.set_resistance(0)
    mot.clean_exit()
