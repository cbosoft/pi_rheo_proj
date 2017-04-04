#
# Motor Speed Control Test
#
# Tries to maintain the speed at a set point using the control library.
#

import sys
sys.path.append('./..')

import motor
import time

# Create instance of motor class
mot = motor.motor(startnow=True, poll_logging=True, log_dir="./logs", filtering="butter", filt_param_B=0.01, i_poll_rate=0.001)

print "Starting..."
mot.set_pot(36)  # roughly 200 RPM
mot.update_setpoint(200)
time.sleep(1)  # wait a bit
mot.start_control()
nu_ca = 36
try:
    for i in range(0, 60):
        sys.stdout.write("\r Time:  {}\tSetpoint:  {}\tError:  {}\tControl action:  {}\tSpeed: {}".format(i + 1, mot.pic.set_point, mot.pic.Es[-1], mot.pic.Us[-1], mot.pic.Ys[-1]))
        sys.stdout.flush()
        time.sleep(1)

    mot.update_setpoint(400.0)
    
    for i in range(0, 60):
        sys.stdout.write("\r Time:  {}\tSetpoint:  {}\tError:  {}\tControl action:  {}\tSpeed: {}".format(i + 61, mot.pic.set_point, mot.pic.Es[-1], mot.pic.Us[-1], mot.pic.Ys[-1]))
        sys.stdout.flush()
        time.sleep(1)

    mot.clean_exit()
except KeyboardInterrupt:
    mot.clean_exit()
