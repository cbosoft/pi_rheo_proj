#
# Motor Speed Control Test
#
# Tries to maintain the speed at a set point using the control library.
#

import sys
sys.path.append('./..')

import motor
import control as cl
import time

log_ = "./control.csv"
logf = open("log_", "w")

# Create instance of motor class
mot = motor.motor(startnow=True, poll_logging=False, filtering="butter")

# Create instance of controller class
controller = cl.PIDcontroller(KP=0.4, KI=9, sample_time=0.1)

controller.set_point = 200.0

print "Starting..."
mot.pot.set_resistance(48)  # roughly 414 RPM
time.sleep(5) # wait 5s

try:
    for i in range(0, 600):
        delta_pv = controller.get_control_action(mot.fdr * mot.svf[0] + mot.svf[1])
        nu_ca = mot.pot.lav + delta_pv
        if nu_ca < 0: nu_ca = 0
        if nu_ca > 127: nu_ca = 127
        logf.write("{0}, {1}, {2}, {3}, {4}".format(time.time(), mot.dr, mot.fdr, delta_pv, nu_ca))
        mot.pot.set_resistance(int(nu_ca))
        # wait
        time.sleep(0.1)
    logf.close()
    mot.clean_exit()
    
    
except KeyboardInterrupt:
    logf.close()
    mot.clean_exit()
