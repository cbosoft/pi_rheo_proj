import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import glob

import pandas as pd
from plothelp import fit_line

def fitf(x, a, b):
    return a * x[0] + b + 0.0156 * x[1]

def fit2f(x, a, b, c):
    return a * x[0] + b + c * x[1]

######################## Calibrate using "Pure" glycerol
# Geometry of the couette cell

roo = 0.044151 / 2.0  # outer cell outer radius in m
ro = 0.039111 / 2.0  # outer cell radius in m
ri = 0.01525  # inner cell radius in m

icxsa = np.pi * (ri ** 2)
ocxsa = np.pi * (ro ** 2)
dxsa = ocxsa - icxsa  # vol per height in m3/m
dxsa = dxsa * 1000 # l / m
dxsa = dxsa * 1000 # ml / m

fill_height = 15 / dxsa

# Reads the data
datf = pd.read_csv("./../../logs/glycerol_long_sweep.csv")

stg = datf['t']
stg = stg - stg[0]
dr = datf['dr']
cr = datf['cr']
pv = datf['pv']

# Filter noise from data
dr = filter(stg, dr, method="butter", A=2, B=0.0001)
cr = filter(stg, cr, method="butter", A=2, B=0.0001)

# Chop off unwanted data
start = 200000
stop = -1 #* (len(cr) - start - 180 * 1000)
skip = 1
stg = stg[start:stop:skip]
dr = dr[start:stop:skip]
cr = cr[start:stop:skip]
pv = pv[start:stop:skip]

# Calculate the required stall torque for these readings
musg    = [1.328] * len(cr)
sp_rpms = dr * 316.451 - 163.091
sp_rads = (sp_rpms * 2 * np.pi) / 60
sn_rpms = 5.13 * pv + 15.275
gam_dot = (sp_rads * ri) / (ro - ri)
tau     = musg * gam_dot
T       = tau * (2 * np.pi * ri * ri * fill_height) 
Ts      = T / (1.0 - (sp_rpms / sn_rpms))
cu      = (25.177 * cr) - 45.264
cub     = 0.00229473 * pv + 0.48960784
vo      = 0.0636 * pv + 2.423

# Relate the stall torque to the current supply
eff, __ =  curve_fit(fit2f, [(cu - cub), vo], T)

# Calculate the viscosity using the read data and the fit
Tg_fc       = eff[0] * (cu - cub) + eff[1] + eff[2] * vo
taug_fc     = Tg_fc / (2 * np.pi * ri * ri * fill_height)
mug_fc = taug_fc / gam_dot



########### Check the calibration using the water run
# Reads the data
datf    = pd.read_csv("./../../logs/water_long_sweep.csv")

stw      = datf['t']
stw      = stw - stw[0]
dr      = datf['dr']
cr      = datf['cr']
pv      = datf['pv']

# Filter noise from data
dr      = filter(stw, dr, method="butter", A=2, B=0.001)
cr      = filter(stw, cr, method="butter", A=2, B=0.001)

# Chop off unwanted data
start   = 200000
stop    = -1 #* (len(cr) - start - 180 * 1000)
skip    = 1
stw      = stw[start:stop:skip]
dr      = dr[start:stop:skip]
cr      = cr[start:stop:skip]
pv      = pv[start:stop:skip]

# Calculate viscosity
musw    = [0.001005] * len(cr)
cu      = (25.177 * cr) - 45.264
cub     = 0.00229473 * pv + 0.48960784
sp_rpms = dr * 316.451 - 163.091
sp_rads = (sp_rpms * 2 * np.pi) / 60
sn_rpms = 5.13 * pv + 15.275
vo      = 0.0636 * pv + 2.423

#T calibration
gam_dotw = (sp_rads * ri) / (ro - ri)
Tw_fc       = eff[0] * (cu - cub) + eff[1] + eff[2] * vo
tauw_fc     = Tw_fc / (2 * np.pi * ri * ri * fill_height) 
muw_fc = tauw_fc / gam_dotw

# Compare with Lab Rheom
mur = [0] * 0
gam_dotr = [0] * 0

# Read csv
datf = pd.read_csv("./../../logs/ref_fluid_rheom_res/g100.csv")
mur.append(datf['mu'])
gam_dotr.append(datf['gam_dot'])

# Plot
f = plt.figure(figsize=(10, 10))
ax = f.add_subplot(111)
ax.plot(stg, musg)
ax.plot(stw, musw)
ax.plot(stg, mug_fc)
ax.plot(stw, muw_fc)
ax.set_yscale('log')
ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)
plt.grid(which='both', axis='both')
plt.savefig("./fig_t_check.png")
