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

finished = False
kp = 0.0
ki = 0.0
kd = 0.0
tun = [kp, ki, kd]

print "control started"

while not finished:
    print "tuning: {}".format(m.pidc.tuning)
    m.update_setpoint(100)
    print "Setpoint 100"
    for i in range(0, 20):
        print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
        sleep(1)
    print "Setpoint 200"
    m.update_setpoint(200)
    for i in range(0, 20):
        print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
        sleep(1)
    r = raw_input("Kp or nothing")
    if len(r) == 0:
        finished = True
    else:
        tun[0] = float(r)
        tun[1] = float(raw_input("Ki"))
        tun[2] = float(raw_input("Kd"))
        m.pidc.tuning = tun
m.clean_exit()
