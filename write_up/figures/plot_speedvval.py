import matplotlib.pyplot as plt
import numpy as np

# Read csv
datf = open("./../lib/test scripts/logs/voltvval.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting
av_volt = [0] * 0
av_spd = [0] * 0
pv = [0] * 0

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 13)
    av_volt.append(float(splt[6]))
    av_spd.append(float(splt[12]))
    pv.append(float(splt[0]))

# Speed v Value
# Set up figure
f = plt.figure(figsize=(7, 7))
ax = f.add_subplot(111)

# Calculate trendline
z = np.polyfit(pv[2:], av_spd[2:], 1)
tl = np.poly1d(z)

# Plot data and trendline
ax.plot(pv, av_spd, 'o', label="$Motor\ Speed$")
ax.plot(pv, tl(pv), 'r--', label="$Fit\ Line:\ SPD = {0:.3f}PV + {1:.3f}$".format(z[0], z[1]))

ax.set_xlabel("\n $Potentiometer\ Value,\ unitless$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Motor\ Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

plt.legend()


# Show plot
plt.savefig("./figures/figspeedvval.png")

# Todo: include read motor speed on graph (as opposed to just actual motor speed)


plt.close(f)

# Voltage v Value
# Set up figure
f = plt.figure(figsize=(7, 7))
ax = f.add_subplot(111)

# Calculate trendline
z = np.polyfit(pv[2:], av_volt[2:], 1)
tl = np.poly1d(z)

# Plot data
ax.plot(pv, av_volt, "o", label="$Motor\ Voltage$")
ax.plot(pv, tl(pv), 'r--', label="$Trendline, VOL = {0:.3f}PV + {1:.3f}$".format(z[0], z[1]))

ax.set_xlabel("\n $Potentiometer\ Value,\ unitless$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Average\ Supply\ Voltage,\ V$\n", ha='center', va='center', fontsize=24)

plt.legend()


# Show plot
plt.savefig("./figures/figvoltvval.png")
