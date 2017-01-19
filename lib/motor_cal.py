#
# Motor Calibration Script
#
# Will return the maximum speed and the minimum speed of the motor
#
#

import motor as mot_r
import time

hall_pin = 16
mag_count = 1
mot = mot_r.motor(0, 0, hall_pin, mag_count, True)

print "getting low end speed limit"
mot.pot.set_resistance(0)

print "waiting..."
time.sleep(10)  # wait 10 seconds

print "speed got"
low_speed = mot.get_speed()

print "getting high end speed limit"
mot.set_resistance(127)

print "waiting..."
time.sleep(10)  # wait 10 seconds

print "speed got"
high_speed = mot.get_speed()

print "results\nhigh: " + str(high_speed) + "\nlow: " + str(low_speed)