#
# Step test
#
# Used to create a step change in the motor's voltage and record the difference
# in the motor's rotational speed in the secodns that follow.
#
# The output from this can be used to generate a FOPDT model of the control
# process, thus allowing the controller to be tuned according to the model.
import sys
sys.path.append('./..')

import motlib
import time
import matplotlib.pyplot as plt

print "setting up..."
mot = motlib.motor(startnow=True)

delay = 1000  # delay before step change occurs, ms
length = 1000  # how long the effects of the step are observed for, ms
time_ = 0  # ms since beginning
log = open("./step_log.csv", "w")
log.close()
xs = [0]*2
ys = [0]*2

log = open("./step_log.csv", "a")

#set starting value
mot.pot.set_resistance(0)

print "starting, pre step"
# pre step data
while (time_ <= delay):
    spd = mot.get_speed()
    log.write(str(time_) + "," + str(spd) + "\n")
    xs.append(time_)
    ys.append(spd)
    time.sleep(0.001)
    time_ += 1

print "stepping up"
# perform the step
mot.pot.set_resistance(64)

print "post step"
# collect the data
while (time_ <= (delay + length)):
    spd = mot.get_speed()
    log.write(str(time_) + "," + str(spd) + "\n")
    xs.append(time_)
    ys.append(spd)
    time.sleep(0.001)
    time_ += 1

log.close()
