import motor
from time import sleep
m= motor.motor()
m.start_poll(name="test.csv", controlled=False)
m.update_setpoint(100)
m.set_pot(6)
print "running motor, pwm filtered in fdr column"
for i in range(0, 30):
    print "speed  {:.3f}    lav  {}".format(m.speed, m.pot.lav)
    sleep(1)
m.clean_exit()
