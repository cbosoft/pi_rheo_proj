import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import glob

import pandas as pd
from plothelp import fit_line

def fitf(x, a, b, c, d):
    return a + b * x[0] + c * x[1] + d * x[0] * x[1]

# Import water and Glycerol data
datw    = pd.read_csv("./../../logs/water_long_sweep.csv")
stw     = np.array(datw['t'])
stw     = stw - stw[0]
drw     = np.array(datw['dr'])
crw     = (np.array(datw['cr2a']) + np.array(datw['cr2b'])) / 2
pvw     = np.array(datw['pv'])
muw     = [0.001005] * len(crw)

datg    = pd.read_csv("./../../logs/glycerol_long_sweep.csv")
stg     = np.array(datg['t'])
stg     = stg - stg[0]
drg     = np.array(datg['dr'])
crg     = np.array(datg['cr'])
crg     = (np.array(datg['cr2a']) + np.array(datg['cr2b'])) / 2
pvg     = np.array(datg['pv'])
mug     = [1.145] * len(crg)
stg = stg + stw[-1]

if True:
    stt     = np.concatenate((stw, stg))
    drt     = np.concatenate((drw, drg))
    crt     = np.concatenate((crw, crg))
    pvt     = np.concatenate((pvw, pvg))
    mut     = np.concatenate((muw, mug))
else:
    stt  = stw
    drt = drw
    crt = crw
    pvt = pvw
    mut = muw

# Geometry of the couette cell
roo     = 0.044151 / 2.0  # outer cell outer radius in m
ro      = 0.039111 / 2.0  # outer cell radius in m
ri      = 0.01525  # inner cell radius in m

icxsa   = np.pi * (ri ** 2)
ocxsa   = np.pi * (ro ** 2)
dxsa    = ocxsa - icxsa  # vol per height in m3/m
dxsa    = dxsa * 1000 # l / m
dxsa    = dxsa * 1000 # ml / m

fill_height = 15 / dxsa  # fill volume = 15ml

# filter data
drt     = filter(stt, drt, method="butter", A=2, B=0.0001)
crt     = filter(stt, crt, method = "butter", A=2, B = 0.0001)

# Calculate stuff
cut     = (25.177 * crt) - 45.264
sp_rpms_t = drt * 316.451 - 163.091
sp_rads_t = (sp_rpms_t * 2 * np.pi) / 60
sn_rpms_t = 5.13 * pvt + 15.275
vot     = 0.0636 * pvt + 2.423
pet     = cut * vot
gam_dot = (sp_rads_t * ri) / (ro - ri)
tau     = mut * gam_dot
T       = tau * (2 * np.pi * ri * ri * fill_height) 
eff, __ =  curve_fit(fitf, [cut, gam_dot], T, p0=[0, 0.0156, 0, 0])
Tfit    = eff[0] + eff[1] * cut + eff[2] * gam_dot + eff[3] * cut * gam_dot
tauf    = Tfit / (2 * np.pi * ri * ri * fill_height) 
mufit   = tauf / gam_dot

print "a = {}\nb = {}\nc = {}\nd = {}".format(eff[0], eff[1], eff[2], eff[3])

# Plot
f = plt.figure()
plt.title(" :O ")
ax = f.add_subplot(111)
#ax.plot(stt, cut)
ax.loglog(stt, mut, 'g-')
ax.loglog(stt, mufit, 'r--')
plt.grid(which='both', axis='both')
plt.savefig("./test.png")
