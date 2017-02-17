import matplotlib.pyplot as plt

#Read logfile
datf = open("./log_0.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists
t = [0] * len(datl)  # Time
rc = [0] * len(datl)  # Running count of number of rotations
sa = [0] * len(datl)  # Speed (avish)
si = [0] * len(datl)  # Speed (insta)
hval = [0] * len(datl)  # Hall effect value
pval = [0] * len(datl)  # Potentiometer value (dictating speed)
st = [0] * len(datl)  # Specific time (time from startor run, not epoch)
dt = [0] * len(datl)  # Time between measurements (should be fairly constant)
ones = [1] * len(datl)  # Just a list of 1s
avsa = [0] * 8  # average speeed (1st method)
avsi = [0] * 8  # average speed (2nd method)
av_c = [0] * 8  # running count used to calculate the average speeds

# Split data into lists for easy use
for i in range(1, len(datl)):
    splt = datl[i].split(",", 5)
    t[i] = float(splt[0])
    rc[i] = float(splt[1])
    si[i] = float(splt[2])
    sa[i] = float(splt[3])
    #hval[i] = float(splt[4])
    pval[i] = int(splt[5])
    
    if (i == 0):
        st[i] = 0
        dt[i] = 0
    else:
        st[i] = t[i] - t[0]
        dt[i] = t[i] - t[i - 1]

# Process data
for i in range(0, len(datl)):
    avsa[pval[i] / 16] += sa[i]
    avsi[pval[i] / 16] += si[i]
    av_c[pval[i] / 16] += 1

less_than_full = False

# Calculate the average speeds for each pot value
for i in range(0, 8):
    avsa[i] = avsa[i] / av_c[i]
    avsi[i] = avsi[i] / av_c[i]

ssm = [0] * 100
sosm = [0] * 100
step = len(datl) / 100

for i in range(0, 100):
    ssm[i] = sa[i * step]
    sosm[i] = si[i * step]

# Plot Data
f = plt.figure(figsize=(15, 15))
ax1 = f.add_subplot(111)
if not less_than_full:
    ax1.plot(range(0, 8), avsa, 'b')
    ax1.plot(range(0, 8), avsi, 'r')
else:
    ax1.scatter(range(0, 128), avsa, 'b')
    ax1.scatter(range(0, 128), avsi, 'r')
ax1.set_xlabel(r'Potentiometer Value, unitless', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'Average Speed, RPM \n(avish = red, insta = blue)', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./Average Speed Compare.png")

# Plot Data
f = plt.figure(figsize=(15, 15))
ax1 = f.add_subplot(111)
l = 100
ax1.plot(range(0, l), sosm[:l], 'b')
ax1.plot(range(0, l), ssm[:l], 'r')
ax1.set_xlabel(r'Time, s E-2', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'Average Speed, RPM', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./HES_speed_compare.png")
