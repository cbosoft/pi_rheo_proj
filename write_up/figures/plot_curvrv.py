import sys

sys.path.append("./../../lib/")

import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import filter

# Read csv

log = "./../../logs/std_sweep.csv"

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
    speed.append(float(splt[2]))
    cr.append(float(splt[3]))
    st.append(float(splt[0]) - tz)
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
f = plt.figure(figsize=(16,8))
ax = f.add_subplot(121)

# Plot data and trendline 1: CRF vs CU
coeffs = np.polyfit(crf[:max_l], cu[:max_l], 1)
xl = np.array([2.3, 2.4])
fit = coeffs[-2] * xl + coeffs[-1]
ax.plot(crf[:max_l], cu[:max_l], 'o')
ax.plot((xl[:max_l]), (fit[:max_l]), 'r--', label="$Trendline, CUR = {0:.3f}CR + {1:.3f}$".format(coeffs[-2], coeffs[-1]))

ax.set_xlabel("\n $Current\ Sensor\ Reading,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Current,\ A$\n", ha='center', va='center', fontsize=24)
plt.legend(loc=4)

ax2 = f.add_subplot(122)

# Plot data 2: CR, CRF vs st
ax2.plot(st, cr, color=(0,0,1,0.5))
ax2.plot(st, crf, 'b')
ax2.set_ylim([2.1, 2.6])
ax2.set_ylabel("$Current\ Sensor\ Reading,\ V$\n", ha='center', va='center', fontsize=24)
ax2.set_xlabel("\n$Time,\ s$", ha='center', va='center', fontsize=24)

# Show plot
print "saving plot"
plt.savefig("./figcurreadcal.png")
plt.close(f)

