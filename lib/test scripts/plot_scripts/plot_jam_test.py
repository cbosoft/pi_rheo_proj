import matplotlib.pyplot as plt
import numpy as np
from glob import glob

# Read csv

log = "./../logs/jam_test.csv"  # gets a list of all csvs in directory

print "opening log {0}".format(log)
datf = open(log, "r")  # opens the latest one
datl = datf.readlines()
datf.close()

# Create lists for sorting

speed = [0] * 0
t = [0] * 0
st = [0] * 0
pv = [0] * 0
mav = [0] * 0

splt = datl[1].split(",", 5)
tz = float(splt[0])

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 5)
    t.append(float(splt[0]))
    speed.append(float(splt[2]))
    st.append(float(splt[0]) - tz)
    pv.append(int(splt[4]))

max_l = 20000
mav_l = 200

for i in range(mav_l - 1, len(speed)):
    rt = 0.0
    for j in range(0, mav_l):
        rt += speed[i - j]
    mav.append(rt / mav_l)

# Speed v Time  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
# Set up figure
f = plt.figure(figsize=(8,8))
ax = f.add_subplot(111)

# Plot data and trendline
ax.plot(st[:max_l], pv[:max_l], 'r--')
ax2 = ax.twinx()

ax2.plot(st[(len(st) - len(mav)):(max_l + (len(st) - len(mav)))], mav[:max_l], '-', label="$Recorded\ Speed\ (Moving\ Average)$")

ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

plt.title("$Moving\ Average\ Samples:\ {0}$".format(mav_l))

# Show plot
print "saving plot"
plt.savefig("./figjamtest.png")
plt.close(f)

