import matplotlib.pyplot as plt

#Read logfile
datf = open("./hall_waveformish.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists
t = [0] * len(datl)
val = [0] * len(datl)

st = [0] * len(datl)
dt = [0] * len(datl)
ones = [1] * len(datl)
cnts = [0] * len(datl)
periods = [0] * 0

# Split data into lists for easy use
for i in range(0, len(datl)):
    splt = datl[i].split(",")
    t[i] = float(splt[0])
    val[i] = float(splt[1])

# Process the data

# invert
for i in range(0, len(datl)):
    if val[i] < 20:
        val[i] = 1
    else:
        val[i] = 0

last_time = 0.0

for i in range(1, len(datl)):
    if val[i] > 0.5 and val[i - 1] < 0.5:  # if rising edge
        if last_time == 0.0:
            last_time = t[i]
        else:
            periods.append(t[i] - last_time)
            last_time = t[i]

# Plot the data (placeholder script)
f = plt.figure(figsize=(25, 25))
ax1 = f.add_subplot(211)
ax1.plot(t[:200], val[:200])
ax1.set_xlabel(r'Time, ms', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'HES High or Low, digital', ha='center',
va='center', fontsize=12)

ax2 = f.add_subplot(212)
ax2.plot(range(0, 10), periods[:10])
ax2.set_xlabel(r'T/P', ha='center',
va='center', fontsize=12)
ax2.set_ylabel(r'Period of Wave', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./hall_wave_graph.png")
