#
# Motor Speed Test Script
#
# Will set the digpot value and hold for some time before moving on to the next
#
# After data is gathered, performs a 1d fit to data
#

import sys
sys.path.append('./..')

#import motor
import time

#mot = motor.motor(startnow=True, poll_logging=True, log_dir="./dynamo_cal", i_poll_rate=0.001)

#print "Starting..."
#mot.pot.set_resistance(48)
#time.sleep(0.5)

#for i in range(0, 128):
#    print "Setting potval to " + str(0 + (i))
#    mot.pot.set_resistance(0 + (i))
#    time.sleep(1)

#mot.clean_exit()


import matplotlib.pyplot as plt
import numpy as np
from glob import glob

# Read csv
log = sorted(glob("./dynamo_cal/*.csv"))[-1]

print "opening log {0}".format(log)
datf = open(log, "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting

t = [0] * 0
st = [0] * 0

rv = [0] * 0
pv = [0] * 0

splt = datl[1].split(",", 5)

for i in range(1, len(datl)):
    splt = datl[i].split(",")
    t.append(float(splt[0]))
    st.append(t[i - 1] - t[0])

    rv.append(float(splt[1]))
    pv.append(int(splt[3]))

# Read csv
datf = open("./../../logs/voltvval.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting
av_volt = [0] * 0
av_spd = [0] * 0
p2v = [0] * 0

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 13)
    av_volt.append(float(splt[6]))
    av_spd.append(float(splt[12]))
    p2v.append(float(splt[0]))

# 1st Trend: speed as a function of potval
zavspdpv = np.polyfit(p2v[4:], av_spd[4:], 1)
tlo = np.poly1d(zavspdpv)

# Set up figure
f = plt.figure(figsize=(7, 7))
ax = f.add_subplot(111)

# 2nd Trend: read voltage as a function of potval
z = np.polyfit(pv, rv, 1)
tl = np.poly1d(z)

# 3rd Trend: speed as a function of read voltage
z3z = np.polyfit(tl(pv), tlo(pv), 1)
t3l = np.poly1d(z3z)

# Plot data and trendline
#ax.plot(rv, av, 'o', label="$Recorded\ Speed$")
ax.plot(tl(pv), t3l(tl(pv)), 'r--', label="$v_{2} = {0:.3f} V_D {1:.3f}$".format(z3z[0], z3z[1], "{NL}"))

ax.set_xlabel("\n $Read Voltage,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

# Show Legend
plt.legend()

# Show plot
plt.savefig("./fig_speed_v_rvolt.png")
