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
    return a * np.log(x[0]) + c

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
datf = pd.read_csv("./../../logs/g9873c.csv")

stg     = datf['t']
stg     = stg - stg[0]
dr      = datf['dr']
cr      = datf['cr']
cr2a    = datf['cr2a']
cr2b    = datf['cr2b']
pv      = datf['pv']

# Filter noise from data
dr = filter(stg, dr, method="butter", A=2, B=0.0001)
cr = filter(stg, cr, method="butter", A=2, B=0.0001)
cr2a = filter(stg, cr2a, method="butter", A=2, B=0.0001)
cr2b = filter(stg, cr2b, method="butter", A=2, B=0.0001)

# Chop off unwanted data
start   = 20000
stop    = -1 * (int(len(cr) * 1) - 25000)
skip    = 1000
stg     = stg[start:stop:skip]
dr      = dr[start:stop:skip]
cr      = cr[start:stop:skip]
cr2a    = cr2a[start:stop:skip]
cr2b    = cr2b[start:stop:skip]
pv      = pv[start:stop:skip]

# Calculate the required stall torque for these readings
musg    = [1.129] * len(cr)
sp_rpms = dr * 316.451 - 163.091
sp_rads = (sp_rpms * 2 * np.pi) / 60
sn_rpms = 5.13 * pv + 15.275
gam_dot = (sp_rads * ri) / (ro - ri)
tau     = musg * gam_dot
T       = tau * (2 * np.pi * ri * ri * fill_height) 

Ts      = T / (1.0 - (sp_rpms / sn_rpms))
cu      = 16.573 * cr - 29.778
cu2a    = 11.307 * cr2a - 29.066
cu2b    = 11.307 * cr2b - 29.066
cub     = 0.00229473 * pv + 0.48960784
cu      = (cu + cu2a + cu2b) / 3
vo      = 0.0636 * pv + 2.423

# Relate the stall torque to the current supply
eff, __ =  curve_fit(fit2f, [(cu - cub)], T)
print eff

# Calculate the viscosity using the read data and the fit #####################################################################################################################################
Tg_fc       = eff[0] * np.log((cu - cub)) + eff[2]
taug_fc     = Tg_fc / (2 * np.pi * ri * ri * fill_height)
mug_fc = taug_fc / gam_dot

f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)
ax.errorbar((cu - cub), T, xerr=(0.05 * np.array(cu)), marker='o', linestyle='None', label="$Required\ Torque$")
ax.plot((cu-cub), ((cu - cub) * eff[0] + eff[1]), label="$T\ =\ {:.3E} * \Delta I_{} + {:.3E}$".format(eff[0], "{ms}", eff[1]))

ax.set_xlabel("\n $\Delta Current,\ A$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Torque,\ Nm$\n", ha='center', va='center', fontsize=24)
#plt.legend(loc=4)
plt.grid(which='both', axis='both')
plt.savefig("./fig_t_cal_log.png")

def check(filename, viscosity, fillvol):
    ########### Check the calibration using the water run
    # Reads the data

    # Geometry of the couette cell

    roo = 0.044151 / 2.0  # outer cell outer radius in m
    ro = 0.039111 / 2.0  # outer cell radius in m
    ri = 0.01525  # inner cell radius in m

    icxsa = np.pi * (ri ** 2)
    ocxsa = np.pi * (ro ** 2)
    dxsa = ocxsa - icxsa  # vol per height in m3/m
    dxsa = dxsa * 1000 # l / m
    dxsa = dxsa * 1000 # ml / m

    fill_height = fillvol / dxsa

    datf = pd.read_csv(filename)

    stw     = datf['t']
    stw     = stw - stw[0]
    dr      = datf['dr']
    cr      = datf['cr']
    cr2a    = datf['cr2a']
    cr2b    = datf['cr2b']
    pv      = datf['pv']

    # Filter noise from data
    dr      = filter(stw, dr, method="butter", A=2, B=0.001)
    cr      = filter(stw, cr, method="butter", A=2, B=0.001)
    cr2a    = filter(stw, cr2a, method="butter", A=2, B=0.001)
    cr2b    = filter(stw, cr2b, method="butter", A=2, B=0.001)

    # Calculate viscosity
    musw    = [viscosity] * len(cr)
    cu      = 16.573 * cr - 29.778
    cu2a    = 11.307 * cr2a - 29.066
    cu2b    = 11.307 * cr2b - 29.066
    cu      = np.array((cu + cu2a + cu2b) / 3)
    cub     = 0.00229473 * pv + 0.48960784
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    vo      = 0.0636 * pv + 2.423

    #T calibration
    gam_dotw    = (sp_rads * ri) / (ro - ri)
    #Tw_fc       = eff[0] * (cu - cub) + eff[1] ##########################################################################################################################################################################################################################################################################
    Tw_fc       = eff[0] * np.log(np.abs(cu - cub)) + eff[2]
    tauw_fc     = Tw_fc / (2 * np.pi * ri * ri * fill_height) 
    muw_fc = tauw_fc / gam_dotw
    return stw, muw_fc, musw

st9873, mufc9873, mus9873 = check("./../../logs/g9873c.csv", 1.129, 15)
st9623, mufc9623, mus9623 = check("./../../logs/g9623c.csv", 0.9061, 15)
st9375, mufc9375, mus9375 = check("./../../logs/g9375c.csv", 0.6102, 15)
st8887, mufc8887, mus8887 = check("./../../logs/g8887c.csv", 0.4005, 15)

# Plot
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)
start = 20000
stop = -1 * (len(st9873) - 115000)
skip = 1000
ax.plot(stg, musg, 'b')
ax.plot(stg, mug_fc, 'bx')

ax.plot(st9375[start:stop:skip], mus9375[start:stop:skip], 'g')
ax.plot(st9375[start:stop:skip], mufc9375[start:stop:skip], 'g^')

ax.plot(st9623[start:stop:skip], mus9623[start:stop:skip], 'r')
ax.plot(st9623[start:stop:skip], mufc9623[start:stop:skip], 'r^')
#ax.set_yscale('log')
ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)
plt.grid(which='both', axis='both')
plt.savefig("./fig_t_check_log.png")
