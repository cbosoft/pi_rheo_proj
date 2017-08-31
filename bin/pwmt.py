import motor
from time import sleep
m= motor.motor()
m.start_poll(name="test.csv", controlled=False)
m.update_setpoint(100)
m.set_pot(6)

m.pwm_er.ChangeDutyCycle(25.0)
for i in range(0, 10):
    print "speed  {:.3f}    dc  0.25".format(m.speed)
    sleep(1)

m.pwm_er.ChangeDutyCycle(50.0)
for i in range(0, 10):
    print "speed  {:.3f}    dc  0.5".format(m.speed)
    sleep(1)

m.pwm_er.ChangeDutyCycle(75.0)
for i in range(0, 10):
    print "speed  {:.3f}    dc  0.75".format(m.speed)
    sleep(1)

m.clean_exit()
