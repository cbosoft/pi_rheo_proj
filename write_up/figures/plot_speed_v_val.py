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
    read_speed.append(312.806 * rv - 159.196)
    read_pv.append(float(splt[3]))

filtered_reading = filter(read_pv, read_speed)

# Speed v Value
# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Calculate trendline
z = np.polyfit(pv, av_spd, 1)
tl = np.poly1d(z)

# Plot data and trendline

#plt.errorbar(pv, av_spd, yerr=av_spd_err, label="$Actual\ Motor\ Speed$", fmt='bx-', ecolor='g')
#ax.plot(read_pv, read_speed, 'go', label='$Read\ Motor\ Speed$')

ax.plot(read_pv, filtered_reading, '.', color=(1,0.5,0.5,1), label="$Filtered\ Speed\ Reading$")
ax.plot(pv, av_spd, 'b-', label="$Actual\ Motor\ Speed$")
ax.plot(pv, tl(pv), 'g--', label="$v_{2} = {0:.3f}pv + {1:.3f}$".format(z[0], z[1], "{NL}"))

ax.set_xlabel("\n $Potentiometer\ Value,\ unitless$", ha='center', va='center', fontsize=24)
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
theo_volt = np.multiply(pv, 0.0636) + 2.423
ax.plot(pv, theo_volt, "x", label="$Theoretical\ Voltage$")
#ax.plot(pv, av_volt, "o")
plt.errorbar(pv, av_volt, yerr=av_volt_err, label="$Motor\ Voltage$", fmt='o', ecolor='g', color='g')
ax.plot(pv, tl(pv), 'r--', label="$V_{2} = {0:.3f}pv + {1:.3f}$".format(z[0], z[1], "{ms}"))

ax.set_xlabel("\n $Potentiometer\ Value,\ unitless$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Average\ Supply\ Voltage,\ V$\n", ha='center', va='center', fontsize=24)

plt.legend(loc=4)


# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_supplyvolt_v_val.png")
