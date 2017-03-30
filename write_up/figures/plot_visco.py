import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
import numpy as np

# Read csv

log = "./../../logs/long_cal.csv"
datf = open(log, "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting

t = [0] * 0
st = [0] * 0

cr = [0] * 0
dr = [0] * 0
pv = [0] * 0

cu = [0] * 0
sp_rpms = [0] * 0
sp_rads = [0] * 0
sn_rpms = [0] * 0
Ts = [0] * 0
T = [0] * 0
tau = [0] * 0
gam_dot = [0] * 0
mu = [0] * 0
s2t = [0] * 0

roo = 0.044151 / 2.0  # outer cell outer radius in m
ro = 0.039111 / 2.0  # outer cell radius in m
ri = 0.01525  # inner cell radius in m
L = 0.039753 - (roo - ro)  # height of couette cell

splt = datl[1].split(",", 5)
tz = float(splt[0])

for i in range(1, len(datl)):
    splt = datl[i].split(",")
    t.append(float(splt[0]))
    st.append(float(splt[0]) - tz)
    
    dr.append(float(splt[1]))
    cr.append(float(splt[2]))
    pv.append(int(splt[3]))

if True:
    dr = filter(st, dr, method="butter",A=2, B=0.01)
    cr = filter(st, cr, method="butter",A=2, B=0.01)

for i in range(0, len(datl)):
    s2t.append(st[i-1])
    cu.append((cr[i-1] * 3.58) - 7.784)
    sp_rpms.append((dr[i-1] * 312.809) - 159.196)
    sp_rads.append((sp_rpms[-1] * 2 * np.pi) / 60)
    sn_rpms.append(((5.13 * pv[i - 1]) + 15.275))
    #    sn_rpms.append((4.292 * pv[i - 1]) + 144.927)

    #Ts.append((0.14 * cu[-1]) + 0.032)
    Ts.append(0.119)
    T.append(Ts[-1] * (1 - (sp_rpms[-1] * 0.1667 / sn_rpms[-1])))

    tau.append(T[-1] / (2 * np.pi * ri * ri * L))
    
    gam_dot.append(sp_rads[-1] * (ri / (ro - ri)))
    
    mu.append(tau[-1] / gam_dot[-1])

if True:
    mu = filter(st, mu, method="butter", A=2, B=0.01)

exp_visc = [0] * 2
exp_t = [190] * 1
exp_t.append(st[-1])
exp_tau = [0] * 0
exp_tau.append(tau[0])
exp_tau.append(tau[-1])

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Plot data and trendline
ax.plot(s2t[0::100], mu[0::100], 'b.')
ax.plot(exp_t, exp_visc, 'g--')
#ax.set_ylim([-10, 10])
#ax.set_yscale("log")
ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)


# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_visco_v_t.png")
plt.close(f)

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Plot data and trendline
ax.loglog(tau[0::100], mu[0::100], 'b.')
#ax.plot(exp_tau, exp_visc, 'g--')
#ax.plot(sp_rpms, sn_rpms, 'o')
#ax.set_ylim([-10, 10])
#ax.set_yscale("log")
ax.set_xlabel("\n $Shear\ Stress,\ Pa$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)


# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_visco_v_tau.png")

