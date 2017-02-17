import matplotlib.pylot as plt

datf = open("./old/spdvals.csv", "r")
datl = datf.readlines()
datf.close()
vals = [0] * len(datl)
speeds = [0] * len(datl)
for i in range(0, len(datl)):
    splt = datl[i].split(",")
    vals[i] = splt[0]
    speeds[i] = splt[1]
f = plt.figure(figsize=(5, 5))
ax1 = f.add_subplot(111)
ax1.plot(vals, speeds)
ax1.set_xlabel(r'Potentiometer Value, unitless', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'Measured Speed, RPM', ha='center',
va='center', fontsize=12)
plt.savefig("./mot_cal_val_vs_spd.png")
