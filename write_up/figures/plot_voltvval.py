import matplotlib.pyplot as plt
import numpy as np
from glob import glob

# Read csv
datf = open("./../../logs/pulley_test/smallx4.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting

speed = [0] * 0
t = [0] * 0
st = [0] * 0
pv = [0] * 0

splt = datl[1].split(",", 5)
tz = float(splt[0])

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 5)
    t.append(float(splt[0]))
    speed.append(float(splt[2]))
    st.append(float(splt[0]) - tz)
    pv.append(int(splt[4]))

# Read csv
datf = open("./../../logs/voltvval.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting
av_volt = [0] * 0
av_spd = [0] * 0
p2v = [0] * 0

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 13)
    av_volt.append(float(splt[6]))
    av_spd.append(float(splt[12]))
    p2v.append(float(splt[0]))

# 1st Trend: speed as a function of potval
zavspdpv = np.polyfit(p2v[4:], av_spd[4:], 1)
tlo = np.poly1d(zavspdpv)

# Speed v Val  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
# Set up figure
f = plt.figure(figsize=(7, 7))
ax = f.add_subplot(111)

# 2nd Trend: read voltage as a function of potval
z = np.polyfit(pv, speed, 1)
tl = np.poly1d(z)

# 3rd Trend: speed as a function of read voltage
z3z = np.polyfit(tl(pv), tlo(pv), 1)
t3l = np.poly1d(z3z)

# Plot data and trendline
#ax.plot(speed, av, 'o', label="$Recorded\ Speed$")
ax.plot(tl(pv), t3l(tl(pv)), 'r--', label="$Trendline, SPD = {0:.3f}RV + {1:.3f}$".format(z3z[0], z3z[1]))

ax.set_xlabel("\n $Read Voltage,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

# Show Legend
plt.legend()

# Show plot
plt.savefig("./figspeedvrv.png")
plt.close(f)

