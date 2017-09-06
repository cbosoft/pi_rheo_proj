import motor
from time import sleep
m= motor.motor(i_poll_rate=0.001)
m.start_poll(name="test.csv", controlled=False)
#m.update_setpoint(100)
#m.set_pot(6)

for i in range(20, 201):
    dc = i / 2.0
    m.set_dc(dc)
    sleep(0.25)
    print m.volts[1], dc, (dc * 0.005 * 1023)
    sleep(0.25)

m.clean_exit()
