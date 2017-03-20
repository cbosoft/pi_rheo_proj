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
mot = motlib.motor(startnow=True, log_dir="./step_test_filt_g", filtering="gaussian", i_poll_rate=0.001)

delay = 5000  # delay before step change occurs, ms
length = 5000  # how long the effects of the step are observed for, ms
time_ = 0  # ms since beginning
#log = open("./step_log.csv", "w")
#log.close()
#xs = [0]*2
#ys = [0]*2
#start_time = time.time() * 1000.0

#log = open("./step_log.csv", "a")

#set starting value
mot.pot.set_resistance(0)

print "starting, pre step"
# pre step data
#while (time_ <= delay):
#    spd = mot.get_speed()
#    log.write(str(time_) + "," + str(spd) + "\n")
#    xs.append(time_)
#    ys.append(spd)
#    time.sleep(0.001)
#    time_ = (time.time() * 1000.0) - start_time

time.sleep(delay / 1000)

print "stepping up"
# perform the step
mot.pot.set_resistance(64)

time.sleep(length / 1000)

print "post step"
# collect the data
#while (time_ <= (delay + length)):
#    spd = mot.get_speed()
#    log.write(str(time_) + "," + str(spd) + "\n")
#    xs.append(time_)
#    ys.append(spd)
#    time.sleep(0.001)
#    time_ = (time.time() * 1000.0) - start_time

#log.close()
mot.clean_exit()