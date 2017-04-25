import sys

sys.path.append("./../../bin")

from filter import filter
import matplotlib.pyplot as plt
import numpy as np

# Read csv
datf = open("./../../logs/voltvval.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting
av_volt = [0] * 0
av_volt_err = [0] * 0
av_spd = [0] * 0
av_spd_err = [0] * 0
pv = [0] * 0

for i in range(2, len(datl)):
    splt = datl[i].split(",")

    tve = float(splt[5])
    if tve > 0.01:
        av_volt_err.append(tve)
    else:
        av_volt_err.append(0.01)

    av_volt.append(float(splt[6]))
    av_spd.append(float(splt[12]))
    av_spd_err.append(float(splt[13]))
    pv.append(float(splt[0]))

# Read csv
datf = open("./../../logs/long_cal.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists for sorting
read_speed = [0] * 0
read_pv = [0] * 0

for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 13)
    rv = float(splt[1])
    #read_speed.append(float(splt[2]))
    read_speed.append(316.451 * rv - 162.091)
    read_pv.append(float(splt[3]))

filtered_reading = filter(read_pv, read_speed, method="butter", A=2, B=0.001)

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Calculate trendline
z = np.polyfit(pv, av_spd, 1)
tl = np.poly1d(z)

pv = np.array(pv)
read_pv = np.array(read_pv)

stdfv = [0]*0
avfv = [0]*0
for i in range(1, len(filtered_reading[::50000]) - 1):
    stdfv.append(np.std(read_speed[(i * 50000) - 24999:(i * 50000) + 25000]))
    avfv.append(np.average(filtered_reading[(i * 50000) - 24999:(i * 50000) + 25000]))
#filtered_reading[::50000]
# Plot data and trendline
#print len(((read_pv[::50000] * 0.066) + 2.278)[1:-1]), len(stdfv), len(avfv)
ax.errorbar(((read_pv[::50000] * 0.066) + 2.278)[1:-1], avfv, yerr=stdfv, marker='o', linestyle='None', label="$Read Motor Speed$")
#ax.plot((read_pv * 0.066) + 2.278, read_speed, color=(1,0,0,0.1))
ax.plot((pv * 0.066) + 2.278, av_spd, 'b-', label="$Actual\ Motor\ Speed$")
ax.plot((pv * 0.066) + 2.278, tl(pv), 'g--', label="$v_{2} = {0:.3f}pv + {1:.3f}$".format(z[0], z[1], "{NL}"))

ax.set_xlabel("\n $Supply\ Voltage,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Motor\ Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

plt.legend(loc=2)


# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_speed_v_val.png")


plt.close(f)

# Voltage v Value
# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Calculate trendline
z = np.polyfit(pv[2:-2], av_volt[2:-2], 1)
tl = np.poly1d(z)

# Plot data
stdv = np.std(av_volt)
theo_volt = np.multiply(pv, 0.0636) + 2.423
ax.plot(pv, theo_volt, "x", label="$Theoretical\ Voltage$")
plt.errorbar(pv, av_volt, yerr=stdv, label="$Motor\ Voltage$", fmt='o', ecolor='g', color='g')
ax.plot(pv, tl(pv), 'r--', label="$V_{2} = {0:.3f}pv + {1:.3f}$".format(z[0], z[1], "{ms}"))

ax.set_xlabel("\n $Potentiometer\ Value,\ 10-bit$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$V_{ms},\ Supply\ Voltage,\ V$\n", ha='center', va='center', fontsize=24)

plt.legend(loc=4)


# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_supplyvolt_v_val.png")
