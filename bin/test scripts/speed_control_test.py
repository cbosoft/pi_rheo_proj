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



# Create instance of motor class
mot = motor.motor(startnow=True, poll_logging=False, filtering="butter", filt_param_B=0.01)

# Create instance of controller class
controller = cl.PIDcontroller(KP=0.1, KI=0.01)#, sample_time=0.1)

logf = open("control_test_log/{}_{}.csv".format(controller.KP, controller.KI), "w")

controller.set_point = 200.0

print "Starting..."
mot.pot.set_resistance(36)  # roughly 200 RPM
time.sleep(1) # wait a bit

nu_ca = 36
try:
    for i in range(0, 600):
        delta_pv = controller.get_control_action((mot.fdr * mot.svf[0]) + mot.svf[1])
        nu_ca = nu_ca + delta_pv
        if nu_ca < 0: nu_ca = 0
        if nu_ca > 127: nu_ca = 127
        logf.write("{0}, {1}, {2}, {3}, {4} \n".format(time.time(), mot.dr, mot.fdr, delta_pv, nu_ca))
        print ("dr: {1:.3f} \t fdr: {2:.3f}\t dpv: {3:.3f}\t ca: {4:.3f} \te: {5:.3f} \tsp: {6:.3f}".format(time.time(), mot.dr, mot.fdr, delta_pv, nu_ca, controller.e[-1], controller.set_point))
        mot.pot.set_resistance(int(nu_ca))
        time.sleep(0.1)

    controller.set_point = 400.0
    for i in range(0, 600):
        delta_pv = controller.get_control_action((mot.fdr * mot.svf[0]) + mot.svf[1])
        nu_ca = nu_ca + delta_pv
        if nu_ca < 0: nu_ca = 0
        if nu_ca > 127: nu_ca = 127
        logf.write("{0}, {1}, {2}, {3}, {4} \n".format(time.time(), mot.dr, mot.fdr, delta_pv, nu_ca))
        print ("dr: {1:.3f} \t fdr: {2:.3f}\t dpv: {3:.3f}\t ca: {4:.3f} \te: {5:.3f} \tspd: {6:.3f}".format(time.time(), mot.dr, mot.fdr, delta_pv, nu_ca, controller.e[-1], controller.set_point))
        mot.pot.set_resistance(int(nu_ca))
        time.sleep(0.1)

    logf.close()
    mot.clean_exit()
    
    
except KeyboardInterrupt:
    logf.close()
    mot.clean_exit()
