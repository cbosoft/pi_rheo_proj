import motor
from time import sleep
m = motor.motor(i_poll_rate=0.01)
m.start_poll(name="test.csv", controlled=False)
#m.update_setpoint(200.0)
#m.set_pot(6)
print "waiting..."
m.set_dc(15) # approx 100
sleep(10)
#m.pidc.tuning = (0.1, 1.0, 0.0)
#m.update_setpoint(100.0)
#m.start_control()
try:
    for i in range(20, 201):
        #dc = i / 2.0
        #m.set_dc(11)
        sleep(0.25)
        print "r: ", m.r_speed, " f: ", m.f_speed, "dc: ", m.ldc, " ca: ", m.pidc.lov, " e: ", m.pidc.lerr
        sleep(0.25)
except KeyboardInterrupt:
    print "Cancelling.."
except:
    raise

m.clean_exit()
