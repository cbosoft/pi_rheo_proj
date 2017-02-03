#
# Motor Calibration Script
#
# Will record the speed results at a range of potentiometer values (from 0 to 127)
#

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
    datf = open("./spdvals.csv",r")
    datl = datf.readlines()
    datf.close()
    vals = [0] * len(datl)
    speeds = [0] * len(datl)
    for i in range(0, len(datl)):
        splt = datl[i].split(",")
        vals[i] = splt[0]
        speeds[i] = splt[1]
    f = plt.figure(figsize=(5, 5))
    ax1 = f.add_subplot(111)
    ax1.plot(vals, speeds)
    ax1.set_xlabel(r'Potentiometer Value, unitless', ha='center',
    va='center', fontsize=12)
    ax1.set_ylabel(r'Measured Speed, RPM', ha='center',
    va='center', fontsize=12)
    plt.savefig("./mot_cal_val_vs_spd.png")
    
    
except KeyboardInterrupt:
    outp.close()
    mot.clean_exit()
