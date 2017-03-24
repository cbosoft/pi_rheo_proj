import sys

sys.path.append("./../../bin/")

import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import filter
import math

# Read csv

log = "./../../logs/long_cal.csv"

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
pv_s = [0] * 0
mav = [0] * 0

splt = datl[1].split(",", 5)
tz = float(splt[0])

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 5)
    t.append(float(splt[0]))
    st.append(float(splt[0]) - tz)

    cr.append(float(splt[2]))
    pv.append(int(splt[3]))

crf = filter.filter(st, cr, method="butter", A=1, B=0.03)

for p in pv:
    if p == 0:
        cu.append(0.48)
        pv_s.append(0)
    elif p == 8:
        cu.append(0.51)
        pv_s.append(8)
    elif p == 16:
        cu.append(0.53)
        pv_s.append(16)
    elif p == 24:
        cu.append(0.55)
        pv_s.append(24)
    elif p == 32:
        cu.append(0.57)
        pv_s.append(32)
    elif p == 40:
        cu.append(0.59)
        pv_s.append(40)
    elif p == 48:
        cu.append(0.6)
        pv_s.append(48)
    elif p == 56:
        cu.append(0.62)
        pv_s.append(56)
    elif p == 64:
        cu.append(0.63)
        pv_s.append(64)
    elif p == 72:
        cu.append(0.65)
        pv_s.append(72)
    elif p == 80:
        cu.append(0.67)
        pv_s.append(80)
    elif p == 88:
        cu.append(0.69)
        pv_s.append(88)
    elif p == 96:
        cu.append(0.7)
        pv_s.append(96)
    elif p == 104:
        cu.append(0.73)
        pv_s.append(104)
    elif p == 112:
        cu.append(0.73)
        pv_s.append(112)
    elif p == 120:
        cu.append(0.75)
        pv_s.append(120)
    elif p == 128:
        cu.append(0.82)
        pv_s.append(128)

# CU AS A FUNC OF PV
coeffs = np.polyfit(pv_s, cu, 1)  # fit linear equation to data read manually
pvlo = np.arange(0, 128, (128.0 / len(pv)))
pvlo = [math.floor(p) for p in pvlo]
pvlo = np.array(pvlo)
cul = coeffs[0] * pvlo + coeffs[1]

min_l = 10000
max_l = len(pv)

# Set up figure
f = plt.figure(figsize=(12, 12))
ax = f.add_subplot(111)

# Plot data and trendline 1: CRF vs CU
coeffs = np.polyfit(crf[min_l:max_l], cul[min_l:max_l], 3)
xl = np.arange(2.24, 2.31, 0.001)
fit = 0
fit_eqn = "$3D\ fit:\ I_{ms} ="
cf_str = ""
for i in range(0, len(coeffs)):
    fit += coeffs[i] * (xl ** (len(coeffs) - 1 - i))
    if coeffs[i] < 0:
        cf_str = "{:.3f}".format(coeffs[i])
    else:
        cf_str = "+{:.3f}".format(coeffs[i])
    if (len(coeffs) - 1 - i) > 1:
        fit_eqn += " {} \\times V_{}^{}".format(cf_str, "{HES}", "{" + str((len(coeffs) - 1 - i)) + "}")
    elif (len(coeffs) - 1 - i) == 1:
        fit_eqn += " {} \\times V_{}".format(cf_str, "{HES}")
    else:
        fit_eqn += " {}".format(cf_str)

fit_eqn += "$"

ax.plot(cr[min_l:max_l], cul[min_l:max_l], '-', color=(1,0,0,0.25), label="$Unfiltered\ HES\ Reading$")
ax.plot(crf[min_l:max_l], cul[min_l:max_l], '-', color=(0,0,1,0.75), label="$Filtered\ HES\ Reading$")
ax.plot(xl, fit, 'g-', label=fit_eqn)
#ax.plot(xl, fit, 'g-', label="$I_{2} = {0:.3f}V_{3}\ {1:.3f}$".format(coeffs[0], coeffs[1], "{ms}", "{HES}"))
ax.set_xlim([2.1, 2.45])
ax.set_ylim([0.475, 0.82])
ax.set_xlabel("\n $Current\ Sensor\ Reading,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Supply\ Current,\ A$\n", ha='center', va='center', fontsize=24)
plt.legend(loc=1)


# Plot data 2: CR, CRF vs ST
#ax2 = f.add_subplot(122)
#ax2.plot(st, cr, color=(0,0,1,0.5))
#ax2.plot(st, crf, 'b')
#ax2.set_ylim([2.1, 2.6])
#ax2.set_ylabel("$Current\ Sensor\ Reading,\ V$\n", ha='center', va='center', fontsize=24)
#ax2.set_xlabel("\n$Time,\ s$", ha='center', va='center', fontsize=24)

# Save plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_hes_cal.png")
plt.close(f)

