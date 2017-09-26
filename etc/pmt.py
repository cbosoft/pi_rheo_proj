from sys import path
path.append("./../bin/")

import motor
import resx
from time import sleep
m= motor.motor()
m.start_poll(name="test.csv", controlled=False)
m.update_setpoint(100)
m.set_dc(25)
print "wait"
for i in range(0, 3):
    print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
    sleep(1)
m.start_control()
print "controlling"
for i in range(0, 20):
    print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
    sleep(1)
print "new setpoint 200"
m.update_setpoint(200)
for i in range(0, 20):
    print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
    sleep(1)
m.clean_exit()
