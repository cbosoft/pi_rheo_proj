#Read logfile
datf = open("./log.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists
t = [0] * len(datl)
rc = [0] * len(datl)
so = [0] * len(datl)
s = [0] * len(datl)

# Split data into lists for easy use
for i in range(0, len(datl)):
    splt = datl[i].split(",", 3)
    t[i] = splt[0]
    rc[i] = splt[1]
    so[i] = splt[2]
    s[i] = splt[3]

# Process/plot the data (placeholder script)
f = plt.figure(figsize=(5, 5))
ax1 = f.add_subplot(111)
ax1.plot(vals, speeds)
ax1.set_xlabel(r'Potentiometer Value, unitless', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'Measured Speed, RPM', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./mot_cal_val_vs_spd.png")