#
# From a list of responses, gets time span between responses and forms a histogram
#
import matplotlib.pyplot as plt
import numpy as np

#Read logfile
datf = open("./log_hall_13.csv", "r")
datl = datf.readlines()
datf.close()

#maximum number of lines to process from data (for looking at specific sections)
maxlen = 1000
lento = len(datl)
if (maxlen < lento):
    lento = maxlen


# Create lists
t = [0] * lento  # Time
st = [0] * lento  # Specific time (time from start of run, not epoch)
dt = [0] * lento  # Time between measurements (should be fairly constant)

# Split data into lists for easy use
for i in range(0, lento):
    splt = datl[i].split(",", 5)
    t[i] = float(splt[0])

    if (i == 0):
        st[i] = 0
        dt[i] = 0
    else:
        st[i] = t[i] - t[0]
        dt[i] = t[i] - t[i - 1]

# Plot Data
f = plt.figure(figsize=(15, 15))
ax1 = f.add_subplot(111)

# Bins might need tweaking between datasets
bins = np.linspace(-10, 40, 6)

ax1.hist(dt, bins)
ax1.set_xlabel(r'$Interval Time, ms$', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'$Count$', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./interval_histogram_compare.png")
