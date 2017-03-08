import matplotlib.pyplot as plt
import numpy as np
from glob import glob

# Read csv

log = "./../../lib/test scripts/logs/cur_read_get.csv"

print "opening log {0}".format(log)
datf = open(log, "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting

speed = [0] * 0
t = [0] * 0
st = [0] * 0
cr = [0] * 0
cu = [0] * 0
pv = [0] * 0
mav = [0] * 0

splt = datl[1].split(",", 5)
tz = float(splt[0])

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 5)
    t.append(float(splt[0]))
    speed.append(float(splt[2]))
    cr.append(float(splt[3]))
    st.append(float(splt[0]) - tz)
    pv.append(int(splt[4]))

for p in pv:
    if p == 0:
        cu.append(0.48)
    elif p == 8:
        cu.append(0.51)
    elif p == 16:
        cu.append(0.53)
    elif p == 24:
        cu.append(0.55)
    elif p == 32:
        cu.append(0.57)
    elif p == 40:
        cu.append(0.59)
    elif p == 48:
        cu.append(0.6)
    elif p == 56:
        cu.append(0.62)
    elif p == 64:
        cu.append(0.63)
    elif p == 72:
        cu.append(0.65)
    elif p == 80:
        cu.append(0.67)
    elif p == 88:
        cu.append(0.69)
    elif p == 96:
        cu.append(0.7)
    elif p == 104:
        cu.append(0.73)
    elif p == 112:
        cu.append(0.73)
    elif p == 120:
        cu.append(0.75)
    elif p == 128:
        cu.append(0.82)

mav_l = 2
# max_l = 20000
max_l = len(speed) - (mav_l - 1)

for i in range(mav_l - 1, len(speed)):
    rt = 0.0
    for j in range(0, mav_l):
        rt += speed[i - j]
    mav.append(rt / mav_l)

# current reading v current actual #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
# Set up figure
f = plt.figure(figsize=(8,8))
ax = f.add_subplot(111)

# Plot data and trendline
z = np.polyfit(st, cu, 1)
tl = np.poly1d(z)

ax.plot(st[:int(0.8 * len(cu))], cu[:int(0.8 * len(cu))])
#ax.plot(cr, cu)
ax.plot(st, tl(st), 'r--', label="$Trendline, CUR = {0:.3f}CR + {1:.3f}$".format(z[0], z[1]))
#ax2 = ax.twinx()

#ax2.plot(st[(len(st) - len(mav)):(max_l + (len(st) - len(mav)))], mav[:max_l], '-', label="$Recorded\ Speed\ (Moving\ Average)$")

ax.set_xlabel("\n $Current\ Sensor\ Reading,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Current,\ A$\n", ha='center', va='center', fontsize=24)

plt.title("$Moving\ Average\ Samples:\ {0}$".format(mav_l))
plt.legend()
# Show plot
print "saving plot"
plt.savefig("./figcurreadcal.png")
plt.close(f)

