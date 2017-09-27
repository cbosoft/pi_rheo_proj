from sys import path
from matplotlib import use as mpluse
mpluse('Agg')
import matplotlib.pyplot as plt
path.append("./../bin/")

import motor
import resx
from time import sleep
m= motor.motor()
m.start_poll(name="test.csv", controlled=False)
m.update_setpoint(100)
m.set_dc(25)
print "warming up motor"
sleep(2)
m.start_control()

Ku = 4

m.pidc.tuning = (Ku, 0.0, 0.0)
m.pidc.tuning = (1.8, 2.85, 0.0)

errs_ = list()
times = list()

print "control started\ttuning: {}".format(m.pidc.tuning)
m.update_setpoint(100)

print "waiting"
for i in range(0, 1):
    #print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
    sleep(1)
print "recording"
for i in range(0, 2000):
    #print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
    errs_.append(m.pidc.lerr)
    times.append((i * 0.1))
    sleep(0.01)
print "tidying up"
m.clean_exit()


f = plt.figure()
ax = f.add_subplot(111)
ax.plot(times, errs_)
plt.savefig("./zn.png")