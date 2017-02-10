#
# Motor Calibration Script
#
# Will record the speed results at a range of potentiometer values (from 0 to 127)
#
import sys
sys.path.append('./..')

import motor as mot_r
import time
import matplotlib.pyplot as plt

hall_pin = 16
mag_count = 1
mot = mot_r.motor(0, 0, hall_pin, mag_count, True)

print "Starting..."
mot.pot.set_resistance(0)
time.sleep(2)

outp = open("./spdvals.csv", "w"):
linstr = ""
try:
    for i in range(0, 128):
        print "Setting potval to " + str(i)
        linstr = str(i)
        mot.pot.set_resistance(i)
        for j in range(0, 10):
            print "Speed: " + str(mot.cur_speed_other) + "RPM"
            linstr += "," + str(mot.cur_speed_other)
        outp.write(linstr + "\n")
    print "Output saved as \"spdvals.csv\""
    mot.clean_exit()
    outp.close()
    
    
except KeyboardInterrupt:
    print "Saving logs.."
    outp.close()
    mot.clean_exit()
