import sys
sys.path.append("./../../bin")

from filter import filter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from glob import glob

# Read csv
datcsv = pd.read_csv("./../../logs/dual_hes_long100.csv")
st = np.array(datcsv['t'])
st = st - st[0]
rv = np.array(datcsv['dr'])
pv = np.array(datcsv['pv'])

#filter readings
#rv = filter(st, rv, method="butter", A=2, B=0.0001)

# Read csv
datf = open("./../../logs/voltvval.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting
av_volt = [0] * 0
av_spd = [0] * 0
p2v = [0] * 0
std = [0] * 0

for i in range(2, len(datl)):
    splt = datl[i].split(",", 13)
    av_volt.append(float(splt[6]))
    av_spd.append(float(splt[12]))
    p2v.append(float(splt[0]))
    std.append(np.std(np.array([float(splt[7]), float(splt[8]), float(splt[9]), float(splt[10]), float(splt[11])])))

av_speed_long = [0] * 0


cur_pv = pv[0]
pv_indx = 0
for i in range(0, len(pv)):
    for j in range(0, len(p2v)):
        if (pv[i] - p2v[j]) < 8 and (pv[i] - p2v[j]) >= 0:

            pv_indx = j
    av_speed_long.append(av_spd[pv_indx])

rv_t_0 = [0] * 0
rv_t_8 = [0] * 0
rv_t_16 = [0] * 0
rv_t_24 = [0] * 0
rv_t_32 = [0] * 0
rv_t_40 = [0] * 0
rv_t_48 = [0] * 0
rv_t_56 = [0] * 0
rv_t_64 = [0] * 0
rv_t_72 = [0] * 0
rv_t_80 = [0] * 0
rv_t_88 = [0] * 0
rv_t_96 = [0] * 0
rv_t_104 = [0] * 0
rv_t_112 = [0] * 0
rv_t_120 = [0] * 0
rv_t_128 = [0] * 0

av_rvs = np.array([0.0] * len(p2v))
for i in range(0, len(pv)):
    for j in range(0, len(p2v)):
        if pv[i] == p2v[j]:
            if j == 0 : rv_t_0.append(rv[i])
            if j == 1 : rv_t_8.append(rv[i])
            if j == 2 : rv_t_16.append(rv[i])
            if j == 3 : rv_t_24.append(rv[i])
            if j == 4 : rv_t_32.append(rv[i])
            if j == 5 : rv_t_40.append(rv[i])
            if j == 6 : rv_t_48.append(rv[i])
            if j == 7 : rv_t_56.append(rv[i])
            if j == 8 : rv_t_64.append(rv[i])
            if j == 9 : rv_t_72.append(rv[i])
            if j == 10 : rv_t_80.append(rv[i])
            if j == 11 : rv_t_88.append(rv[i])
            if j == 12 : rv_t_96.append(rv[i])
            if j == 13 : rv_t_104.append(rv[i])
            if j == 14 : rv_t_112.append(rv[i])
            if j == 15 : rv_t_120.append(rv[i])
            if j == 16 : rv_t_128.append(rv[i])

# 2d list not working as expected, using manual (long hand) method :@
stdv = [0] * 0

# pv = 0
stdv.append(np.std(rv_t_0))
av_rvs[0] = np.average(rv_t_0)

# pv = 8
stdv.append(np.std(rv_t_8))
av_rvs[1] = np.average(rv_t_8)

# pv = 16
stdv.append(np.std(rv_t_16))
av_rvs[2] = np.average(rv_t_16)

# pv = 24
stdv.append(np.std(rv_t_24))
av_rvs[3] = np.average(rv_t_24)

# pv = 32
stdv.append(np.std(rv_t_32))
av_rvs[4] = np.average(rv_t_32)

# pv = 40
stdv.append(np.std(rv_t_40))
av_rvs[5] = np.average(rv_t_40)

# pv = 48
stdv.append(np.std(rv_t_48))
av_rvs[6] = np.average(rv_t_48)

# pv = 56
stdv.append(np.std(rv_t_56))
av_rvs[7] = np.average(rv_t_56)

# pv = 64
stdv.append(np.std(rv_t_64))
av_rvs[8] = np.average(rv_t_64)

# pv = 72
stdv.append(np.std(rv_t_72))
av_rvs[9] = np.average(rv_t_72)

# pv = 80
stdv.append(np.std(rv_t_80))
av_rvs[10] = np.average(rv_t_80)

# pv = 88
stdv.append(np.std(rv_t_88))
av_rvs[11] = np.average(rv_t_88)

# pv = 96
stdv.append(np.std(rv_t_96))
av_rvs[12] = np.average(rv_t_96)

# pv = 104
stdv.append(np.std(rv_t_104))
av_rvs[13] = np.average(rv_t_104)

# pv = 112
stdv.append(np.std(rv_t_112))
av_rvs[14] = np.average(rv_t_112)

# pv = 120
stdv.append(np.std(rv_t_120))
av_rvs[15] = np.average(rv_t_120)

# pv = 128
stdv.append(np.std(rv_t_128))
av_rvs[16] = np.average(rv_t_128)
    
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
ax.plot(tl(pv), t3l(tl(pv)), 'r-', label="$v_{2} = {0:.3f} V_D {1:.3f}$".format(z3z[0], z3z[1], "{m}"))

ax.errorbar(av_rvs, av_spd, yerr=std, xerr=stdv, linestyle='None', marker='o', label="$Logged Data$")

ax.set_xlabel("\n $V_D,\ Dynamo\ Voltage,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$\omega,\ Motor\ Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

# Show Legend
plt.legend(loc=4)

# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_speed_v_rvolt.png")
plt.close(f)
