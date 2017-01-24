#
# Step test
#
# Used to create a step change in the motor's voltage and record the difference
# in the motor's rotational speed in the secodns that follow.
#
# The output from this can be used to generate a FOPDT model of the control
# process, thus allowing the controller to be tuned according to the model.

import motor as mot_r
import time
import matplotlib.pyplot as plt

hall_pin = 16
mag_count = 1
mot = mot_r.motor(0, 0, hall_pin, mag_count, True)

delay = 5000  # ms
length = 5000  # ms
time_ = 0  # ms since beginning
log = open("./step_log.csv", "w")
log.close()
xs = [0]*2
ys = [0]*2

log = open("./step_log.csv", "a")

#set starting value
mot.pot.set_resistance(0)

# pre step data
while (time_ <= delay):
    spd = mot.get_speed()
    log.write(str(time_) + "," + str(spd))
    xs.append(time_)
    ys.append(spd)
    time.sleep(0.001)
    time_ += 1

# perform the step
mot.pot.set_resistance(64)

# collect the data
while (time_ <= (delay + length)):
    spd = mot.get_speed()
    log.write(str(time_) + "," + str(spd))
    xs.append(time_)
    ys.append(spd)
    time.sleep(0.001)
    time_ += 1

log.close()

plt.plot(xs, ys)
plt.show()
