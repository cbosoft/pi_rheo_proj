import sys
sys.path.append("./../../bin")

from filter import filter
import matplotlib.pyplot as plt
import numpy as np
from glob import glob

# Read csv
#datf = open("./../../logs/pulley_test/smallx4.csv", "r")
datf = open("./../../logs/long_cal.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting

rv = [0] * 0
t = [0] * 0
st = [0] * 0
pv = [0] * 0

splt = datl[1].split(",", 5)
tz = float(splt[0])

for i in range(1, len(datl)):
    splt = datl[i].split(",", 5)
    t.append(float(splt[0]))
    st.append(float(splt[0]) - tz)

    rv.append(float(splt[1]))
    pv.append(int(splt[3]))

rv = filter(st, rv, method="butter")
rv = rv[100:]
pv = pv[100:]

# Read csv
datf = open("./../../logs/voltvval.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting
av_volt = [0] * 0
av_spd = [0] * 0
p2v = [0] * 0

for i in range(2, len(datl)):
    splt = datl[i].split(",", 13)
    av_volt.append(float(splt[6]))
    av_spd.append(float(splt[12]))
    p2v.append(float(splt[0]))

av_speed_long = [0] * 0

cur_pv = pv[0]
j = 0
for i in range(0, len(pv)):
    if (pv[i] > (cur_pv + 7)):
        cur_pv = pv[i]
        j += 1
    
    av_speed_long.append(av_spd[j])
    

# 1st Trend: speed as a function of potval
zavspdpv = np.polyfit(p2v[4:], av_spd[4:], 1)
tlo = np.poly1d(zavspdpv)

# Speed v Val  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# 2nd Trend: read voltage as a function of potval
z = np.polyfit(pv, rv, 1)
tl = np.poly1d(z)

# 3rd Trend: speed as a function of read voltage
z3z = np.polyfit(tl(pv), tlo(pv), 1)
t3l = np.poly1d(z3z)

# Plot data and trendline
ax.plot(rv, av_speed_long, 'o', label="$Recorded\ Speed$")
ax.plot(tl(pv), t3l(tl(pv)), 'r--', label="$v_{2} = {0:.3f} V_D {1:.3f}$".format(z3z[0], z3z[1], "{NL}"))

ax.set_xlabel("\n $Read\ Voltage,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

# Show Legend
plt.legend()

# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_speed_v_rvolt.png")
plt.close(f)
