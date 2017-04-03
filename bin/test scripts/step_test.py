#
# Step test
#
# Used to create a step change in the motor's voltage and record the difference
# in the motor's rotational speed in the secodns that follow.
#
# The output from this can be used to generate a FOPDT model of the control
# process, thus allowing the controller to be tuned according to the model.
import sys
sys.path.append('./..')

import motor
import time
import matplotlib.pyplot as plt

print "setting up..."
mot = motor.motor(startnow=True, log_dir="./step_test", filtering="butter", i_poll_rate=0.001)
mot.set_pot(0)

for i in range(0, 5):
    print "waiting..."
    time.sleep(15)
    print "stepping..."
    mot.set_pot(i * 32)

print "waiting..."
time.sleep(15)
mot.clean_exit()
