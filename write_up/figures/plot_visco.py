import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
import numpy as np
import glob

import pandas as pd

# Read csv

#log = "./../../logs/long_cal.csv"
datf = pd.read_csv(sorted(glob.glob("./../../bin/test scripts/long_sweep/*.csv"))[-1])

# Cell geometry
roo = 0.044151 / 2.0  # outer cell outer radius in m
ro = 0.039111 / 2.0  # outer cell radius in m
ri = 0.01525  # inner cell radius in m
L = 0.039753 - (roo - ro)  # height of couette cell

# Split up csv columns
t = datf['t']
st = t - t[0]
dr = datf['dr']
cr = datf['cr']
pv = datf['pv']

# Filtering: aye or naw?
if True:
    dr = filter(st, dr, method="butter",A=2, B=0.001)
    cr = filter(st, cr, method="butter",A=2, B=0.001)

# Calculate viscosity etc
cu = cr * 3.58 - 7.784
sp_rpms = dr * 312.809 - 159.196
sp_rads = (sp_rpms * 2 * np.pi) / 60
sn_rpms = 5.13 * pv + 15.275
Ts = 0.14 * cu + 0.032
T = Ts * (1 - (sp_rpms / sn_rpms))
tau = T / (2 * np.pi * ri * ri * L)
gam_dot = (sp_rads * ri) / (ro - ri)
mu = tau / gam_dot

# Again wi the filtering?
if True:
    mu = filter(st, mu, method="butter", A=2, B=0.001)

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Plot data and trendline
ax.plot(st[10000:], mu[10000:], 'b-')

cr = np.array(cr)
dr = np.array(dr)

ax.set_ylim([-10, 10])
ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)


# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_visco_v_t_.png")
plt.close(f)

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Plot data and trendline
ax.loglog(tau, mu, 'b-')
ax.set_xlabel("\n $Shear\ Stress,\ Pa$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)


# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_visco_v_tau_.png")

