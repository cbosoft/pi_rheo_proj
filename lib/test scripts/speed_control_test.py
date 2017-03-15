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
    r = "./eval_speed_control_test"
else:
    r = "./" + r

# Create instance of motor class
mot = motlib.motor(startnow=True, poll_logging=True, log_dir=r)
#mot = motlib.motor(startnow=True, poll_logging=True, log_dir=r, filtering="butter")

# Create instance of controller class
controller = cl.PIDcontroller(KP=1, KI=1, sample_time=0.1)

# Get setpoint
print "Enter set point motor speed (in RPM):"
print "(Or leave blank for default (200)"

r = raw_input()

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
        nu_ca = mot.pot.lav + delta_pv
        if nu_ca < 0: nu_ca = 0
        print ("applying control action: dPV = {0}, ca = {1}".format(delta_pv, nu_ca))
        mot.pot.set_resistance(int(nu_ca))
        # wait
        time.sleep(0.1)
    mot.clean_exit()
    
except KeyboardInterrupt:
    mot.clean_exit()
