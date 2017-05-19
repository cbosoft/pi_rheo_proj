import sys

sys.path.append("./../bin/")

import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import filter
import math
import pandas as pd
from plothelp import fit_line

# Read csv
#datf = pd.read_csv("./../logs/dual_hes_long1000.csv")
datf = pd.read_csv("./../logs/sensor_calibration_100417.csv")
st      = np.array(datf['t'])
st      = st - st[0]
cr      = np.array(datf['cr'])
cra     = np.array(datf['cr2a'])
crb     = np.array(datf['cr2b'])
cr      = 0.5 * (cra + crb)
cra     = filter.filter(st, cra, method="butter", A=2, B=0.001)
crb     = filter.filter(st, crb, method="gaussian", A=100, B=100)
pv      = np.array(datf['pv'])
crf     = 0.5 * (cra + crb)

cu = [0] * 0
pv_s = [0] * 0

# From manual ammeter read
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

# Remove unwanted outlying data
min_l = 0  #10000
max_l = -1
skip = 1  #0000
cr = cr[min_l:max_l:skip]
crf = crf[min_l:max_l:skip]
cul = cul[min_l:max_l:skip]

crstd = np.std(cr)
crfstd = np.std(crf)

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Plot data and trendline: CRF vs CU
fit, fit_eqn, coeffs = fit_line(crf, cul, 1, x_name="V_{HES}", y_name="I_{ms}")

ax.errorbar(crf, cul, xerr=crfstd, marker='o', linestyle='None', color=(0,0,1,0.75), label="$Filtered\ HES\ Reading$")
ax.plot(crf, fit, 'g-', label=fit_eqn)

ax.set_xlabel("\n $V_{HES},\ Current\ Sensor\ Voltage,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$I_{ms},\ Supply\ Current,\ A$\n", ha='center', va='center', fontsize=24)

plt.legend(loc=4)

plt.grid(which='both', axis='both')
plt.savefig("./fig_dual_hes_cal.png")
plt.close(f)

