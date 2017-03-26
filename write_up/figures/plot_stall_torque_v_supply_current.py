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

z = np.polyfit(cu, st, 1)
tl = np.poly1d(z)

# Plot data and trendline
ax.plot(cu, st, 'o', label="$Read\ Data$")
ax.plot(cu, tl(cu), 'r--', label="$T_S = {0:.3f}I_{1} + {2:.3f}$".format(z[0], "{ms}", z[1]))

ax.set_xlabel("\n $Current\ Supply,\ A$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Stall\ Torque,\ Nm$\n", ha='center', va='center', fontsize=24)

# Show Legend
plt.legend(loc=3)

# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_stall_torque_v_supply_current.png")
plt.close(f)
