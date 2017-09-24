import motor
from time import sleep
m= motor.motor()
m.start_poll(name="test.csv", controlled=False)
m.update_setpoint(100)
m.set_pot(6)
print "wait"
for i in range(0, 3):
    print "speed  {:.3f}    lav  {}".format(m.speed, m.pot.lav)
    sleep(1)
m.start_control()
print "controlling"
for i in range(0, 20):
    print "speed  {:.3f}    lav  {}".format(m.speed, m.pot.lav)
    sleep(1)
print "new setpoint 200"
m.update_setpoint(200)
for i in range(0, 20):
    print "speed  {:.3f}    lav  {}".format(m.speed, m.pot.lav)
    sleep(1)
print "new setpoint 10"
m.update_setpoint(10)
for i in range(0, 20):
    print "speed  {:.3f}    lav  {}".format(m.speed, m.pot.lav)
    sleep(1)
m.clean_exit()
