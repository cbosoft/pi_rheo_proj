import sys

sys.path.append("./..")

import motlib
import time

mot = motlib.motor(startnow=True, log_dir="./torq_get")

mot.pot.set_resistance(0)

r = raw_input("WHAT SPEED? ")

mot.pot.set_resistance(int(r))

r = raw_input("PRESS ENTER TO FINISH")

mot.pot.set_resistance(0)
mot.clean_exit()
