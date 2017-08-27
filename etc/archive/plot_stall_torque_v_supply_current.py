import sys
sys.path.append("./../bin")
from plothelp import fit_line

import matplotlib.pyplot as plt
import numpy as np
from glob import glob

# Read csv
datf = open("./../../logs/stall_torque_v_current.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting

cu = [0] * 0  # supply current, A
bl = [0] * 0  # balance load, g
fo = [0] * 0  # force, N
st = [0] * 0  # stall torque, Nm



for i in range(1, len(datl)):
    splt = datl[i].split(",")
    cu.append(float(splt[0]))
    bl.append(float(splt[1]))

    fo.append(bl[i-1] * 9.80665 * 0.001)
    st.append(fo[i-1] * 0.099375)  # ish

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Get trendline
xl = np.arange(1.05, 2.99, 0.001)
z = np.polyfit(cu, st, 2)
#tl = np.poly1d(z)

fit_eqn = "$2D\ fit:\ T_s ="
cf_str = ""
fit = 0
for i in range(0, len(z)):
    fit += z[i] * (xl ** (len(z) - 1 - i))
    if z[i] < 0:
        cf_str = "{:.3f}".format(z[i])
    else:
        cf_str = "+{:.3f}".format(z[i])
    if (len(z) - 1 - i) > 1:
        fit_eqn += " {} \\times I_{}^{}".format(cf_str, "{ms}", "{" + str((len(z) - 1 - i)) + "}")
    elif (len(z) - 1 - i) == 1:
        fit_eqn += " {} \\times I_{}".format(cf_str, "{ms}")
    else:
        fit_eqn += " {}".format(cf_str)

fit_eqn += "$"

fit, fit_eqn, __ = fit_line(cu, st, 1, "I_{ms}", "Ts")

# Plot data and trendline
ststd = np.std(st)
ax.errorbar(cu, st, yerr=ststd, marker='o', linestyle='None', label="$Read\ Data$")
ax.plot(cu, fit, 'g-', label=fit_eqn)

ax.set_xlabel("\n $I_{ms},\ Current\ Supply,\ A$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$T_S,\ Stall\ Torque,\ N\,m$\n", ha='center', va='center', fontsize=24)

# Show Legend
plt.legend(loc=1)

# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_stall_torque_v_supply_current.png")
plt.close(f)
