from sys import path

path.append("./../bin/")

import motor
from time import sleep
import numpy as np

import resx

m = motor.motor()
m.start_poll(name="test.csv", controlled=False)
#m.update_setpoint(200.0)
#m.set_pot(6)
print "waiting..."
m.set_dc(30) # approx 100
sleep(2)
#m.pidc.tuning = (0.1, 1.0, 0.0)
#m.update_setpoint(100.0)
#m.start_control()
currents = list()
volts = list()
try:
    for i in range(0, 9):
        for j in range(0, 10):
            dc = 10 #+ (i * 10)
            m.set_dc(dc)
            sleep(0.25)
            s = m.speeds
            print "r0: ", s[0], " f0: ", s[1], "r1: ", s[2], "f1: ", s[3], "r2: ", s[0], "f2: ", s[0], "dc: ", m.ldc
            #current = resx.get_current(m.volts[2])
            #volt = m.volts[7] * 1.0
            #currents.append(current)
            #volts.append(volt)
            #"cra: ", m.volts[1], "crb: ", m.volts[2], 
            #print "I: ", current, " V: ", volt, " i: ", i
            sleep(0.25)
except KeyboardInterrupt:
    print "Cancelling.."
except:
    raise

m.clean_exit()
