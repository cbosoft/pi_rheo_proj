import motor
from time import sleep
m= motor.motor()
m.start_poll(name="test.csv", controlled=False)
m.update_setpoint(100)
m.set_pot(6)

#for i in range(0, 200):
#    m.pwm_er.ChangeDutyCycle(i * 0.5)
#    sleep(0.5)
#    print m.volts[1], (i * 0.5)
#    sleep(0.5)

m.pwm_er.ChangeDutyCycle(100)
sleep(10)
m.clean_exit()
