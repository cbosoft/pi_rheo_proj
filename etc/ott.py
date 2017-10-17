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
    while (True):
        for i in range(0, 9):
            dc = 10 #+ (i * 10)
            m.set_dc(dc)
            sleep(0.25)
            s = m.speeds
            print s#s[0], s[1], s[2], s[3], s[4], s[5]#, m.ldc
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
