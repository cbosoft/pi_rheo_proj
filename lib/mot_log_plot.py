import matplotlib.pyplot as plt

#Read logfile
datf = open("./log.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists
t = [0] * len(datl)
rc = [0] * len(datl)
so = [0] * len(datl)
s = [0] * len(datl)
st = [0] * len(datl)
dt = [0] * len(datl)
ones = [1] * len(datl)
cnts = [0] * len(datl)

# Split data into lists for easy use
for i in range(0, len(datl)):
    splt = datl[i].split(",", 3)
    t[i] = float(splt[0])
    rc[i] = float(splt[1])
    so[i] = float(splt[2])
    s[i] = float(splt[3])
    
    if (i ==0):
        st[i] = 0
        dt[i] = 0
    else:
        st[i] = t[i] - t[0]
        dt[i] = t[i] - t[i - 1]

for i in range(0, 100):
    for j in range(0, 100):
        if dt[i] == dt[j]:
            cnts[i] += 1

# Process/plot the data (placeholder script)
f = plt.figure(figsize=(25, 25))
ax1 = f.add_subplot(111)
ax1.scatter(dt[1:100], cnts[1:100])
ax1.set_xlabel(r'Time, s', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'HES High or Low, digital', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./mot_log_graph.png")
