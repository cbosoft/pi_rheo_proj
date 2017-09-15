import motor
from time import sleep
import numpy as np
m = motor.motor(i_poll_rate=0.01)
m.start_poll(name="test.csv", controlled=False)
#m.update_setpoint(200.0)
#m.set_pot(6)
print "waiting..."
m.set_dc(30) # approx 100
sleep(10)
#m.pidc.tuning = (0.1, 1.0, 0.0)
#m.update_setpoint(100.0)
#m.start_control()
try:
    for i in range(0, 9):
        for j in range(0, 10):
            dc = 10 + (i * 10)
            m.set_dc(dc)
            sleep(0.25)
            f = m.f_speeds
            r = m.r_speeds
            print "r0: ", r[0], " f0: ", f[0], "r1: ", r[1], "f1: ", f[1], "r2: ", r[2], "f2: ", f[2], "dc: ", m.ldc
            sleep(0.25)
except KeyboardInterrupt:
    print "Cancelling.."
except:
    raise

m.clean_exit()
