#
# Motor Speed Test Script
#
# Will set the digpot value and hold for some time before moving on to the next
#

import sys
sys.path.append('./..')

import motor
import time

mot = motor.motor(startnow=True, poll_logging=True, log_dir="./cur_sweep", i_poll_rate=0.001)

print "Starting..."
mot.pot.set_resistance(48)
time.sleep(0.5)
for i in range(0, 128):
    print "Setting potval to " + str(0 + (i))
    mot.pot.set_resistance(0 + (i))
    time.sleep(5)
mot.clean_exit()

import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import filter

# Read csv

log = sorted(glob("./cur_sweep/*.csv"))[-1]

print "opening log {0}".format(log)
datf = open(log, "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting

speed = [0] * 0
t = [0] * 0
st = [0] * 0
cr = [0] * 0
cu = [0] * 0
pv = [0] * 0
mav = [0] * 0

splt = datl[1].split(",", 5)
tz = float(splt[0])

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 5)
    t.append(float(splt[0]))
    st.append(t[i - 1] - t[0])

    cr.append(float(splt[3]))
    pv.append(int(splt[4]))

crf = filter.filter(st, filter.filter(st, cr, method="butter"), method="gaussian")

for p in pv:
    if p == 0:
        cu.append(0.48)
    elif p == 8:
        cu.append(0.51)
    elif p == 16:
        cu.append(0.53)
    elif p == 24:
        cu.append(0.55)
    elif p == 32:
        cu.append(0.57)
    elif p == 40:
        cu.append(0.59)
    elif p == 48:
        cu.append(0.6)
    elif p == 56:
        cu.append(0.62)
    elif p == 64:
        cu.append(0.63)
    elif p == 72:
        cu.append(0.65)
    elif p == 80:
        cu.append(0.67)
    elif p == 88:
        cu.append(0.69)
    elif p == 96:
        cu.append(0.7)
    elif p == 104:
        cu.append(0.73)
    elif p == 112:
        cu.append(0.73)
    elif p == 120:
        cu.append(0.75)
    elif p == 128:
        cu.append(0.82)

max_l = 650

# Set up figure
f = plt.figure(figsize=(8,8))
ax = f.add_subplot(111)

# Fit 1: CRF vs CU
coeffs = np.polyfit(crf[:max_l], cu[:max_l], 1)
xl = np.array([2.3, 2.4])
fit = coeffs[-2] * xl + coeffs[-1]

# Plot CU vs filtered CR
ax.plot(crf[:max_l], cu[:max_l], 'o')

# Plot Fit vs CR
ax.plot((xl[:max_l]), (fit[:max_l]), 'r--', label="$I_{2} = {0:.3f}V_{3}\ {1:.3f}$".format(coeffs[-2], coeffs[-1], "{ms}", "{HES}"))

ax.set_xlabel("\n $Current\ Sensor\ Reading,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Actual\ Supply\ Current,\ A$\n", ha='center', va='center', fontsize=24)
plt.legend(loc=4)

print "saving plot"
plt.savefig("./fig_hes_cal.png")
