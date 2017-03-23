import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
import numpy as np

# Read csv

log = "./../../logs/std_sweep.csv"
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
    cr.append(float(splt[3]))
    pv.append(int(splt[4]))

if True:
    dr = filter(st, dr)
    cr = filter(st, cr)

for i in range(1, len(datl)):
    cu.append((cr[i-1] * 3.58) - 7.784)
    sp_rpms.append((dr[i-1] * 317.666) - 146.947)
    sp_rads.append(sp_rpms[i - 1] / (2 * np.pi * 60))
    sn_rpms.append((4.292 * pv[i - 1]) + 144.927)

    Ts.append((0.169 * cu[i - 1]) + 0.038)
    T.append(Ts[i - 1] * (1 - ((sp_rads[i - 1] * 2 * np.pi * 60) / (4.292 * pv[i - 1] + 144.927))))

    tau.append(T[i - 1] / (2 * np.pi * ri * ri * L))
    
    gam_dot.append(sp_rads[i - 1] * ri / (ro - ri))
    
    mu.append(tau[i - 1] / gam_dot[i - 1])

if False:
    mu = filter(st, mu)


# Set up figure
f = plt.figure(figsize=(7, 7))
ax = f.add_subplot(111)
plt.title("Placeholder graph!")
# Plot data and trendline
ax.plot(st, mu, 'b')

ax2 = ax.twinx()
ax2.plot(st, T, 'g')

#ax3 = ax2.twinx()
#ax3.plot(st, Ts, 'r')

#ax4 = ax3.twinx()
#ax4.plot(st, cu, 'o')

ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)


# Show plot
plt.savefig("./visco.png")

