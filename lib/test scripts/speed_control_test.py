#
# Motor Speed Control Test
#
# Tries to maintain the speed at a set point using the control library.
#

import sys
sys.path.append('./..')

import motlib
import control as cl
import time

# Get log directory name
print "Enter the log directory name:"
print "(Or leave blank for default)"

r = raw_input()

if r == "":
    pass
else:
    r = "/" + r

mot = motlib.motor(startnow=True, poll_logging=True, log_dir="./logs" + r)
controller = cl.PIDcontroller(KP=1, KI=1, sample_time=0.1)
# Get setpoint
print "Enter set point motor speed (in RPM):"
print "(Or leave blank for default (200)"

r = raw_input()

# Variables
set_point = 0.0
cur_speed = 0.0


if r == "":
    controller.set_point = 200.0
else:
    controller.set_point = float(r)



print "Starting..."
mot.pot.set_resistance(48)  # roughly 414 RPM
time.sleep(5) # wait 5s


try:
    for i in range(0, 600):
        # for 1 minute:
        # get motor speed
        cur_speed = mot.speed
        # compare with set point & get control action (thank you controller library)
        delta_pv = controller.get_control_action(cur_speed)
        # apply control action
        mot.pot.set_resistance(mot.pot.lav + delta_pv)
        # wait
        time.sleep(0.1)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
