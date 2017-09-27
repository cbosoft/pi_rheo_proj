from sys import path
import matplotlib.pyplot as plt
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

errs_low = list()
time_low = list()
errs_high = list()
time_high = list()

length = 10.0
step = 0.1

print "control started"

while not finished:
    try:
        print "tuning: {}".format(m.pidc.tuning)
        m.update_setpoint(100)
        print "Setpoint 100"
        for i in range(0, 100):
            print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
            errs_low.append(m.pidc.lerr)
            time_low.append((i * step))
            sleep(0.1)
        print "Setpoint 200"
        m.update_setpoint(200)
        for i in range(0, 100):
            print "speed  {:.3f}  gd {:.3f}  lav  {} err {}".format(m.speed, resx.get_strain((m.speed * 2 * 3.14) / 60.0), m.ldc, m.pidc.lerr)
            errs_high.append(m.pidc.lerr)
            time_high.append((i * step))
            sleep(0.1)
        f = plt.figure()
        ax = f.add_subplot(111)
        ax.plot(time_low, errs_low)
        ax.plot(time_high, errs_high, "x")
        plt.show()
    except:
        pass
    print "Old Tuning: ", m.pidc.tuning, "\nNew tuning:"
    r = raw_input("Kp: ")
    if len(r) == 0:
        finished = True
    else:
        tun[0] = float(r)
        tun[1] = float(raw_input("Ki: "))
        tun[2] = float(raw_input("Kd: "))
        m.pidc.tuning = tun
m.clean_exit()
