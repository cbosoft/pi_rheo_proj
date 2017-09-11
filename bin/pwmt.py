import motor
from time import sleep
m = motor.motor(i_poll_rate=0.01)
m.start_poll(name="test.csv", controlled=False)
#m.update_setpoint(100)
#m.set_pot(6)
try:
    for i in range(20, 201):
        dc = i / 2.0
        m.set_dc(dc)
        sleep(0.25)
        print "r: ", m.r_speed, " f: ", m.f_speed, "dc: ", dc
        sleep(0.25)
except KeyboardInterrupt:
    print "Cancelling.."
except:
    raise

m.clean_exit()
