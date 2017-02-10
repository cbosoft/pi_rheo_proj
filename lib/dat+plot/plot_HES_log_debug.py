import matplotlib.pyplot as plt

#Read logfile
datf = open("./log_0.csv", "r")
datl = datf.readlines()
datf.close()

# Create lists
t = [0] * len(datl)  # Time
rc = [0] * len(datl)  # Running count of number of rotations
so = [0] * len(datl)  # Speed, method one
s = [0] * len(datl)  # Speed, method two
hval = [0] * len(datl)  # Hall effect value
pval = [0] * len(datl)  # Potentiometer value (dictating speed)
st = [0] * len(datl)  # Specific time (time from startor run, not epoch)
dt = [0] * len(datl)  # Time between measurements (should be fairly constant)
ones = [1] * len(datl)  # Just a list of 1s
avs = [0] * 128  # average speeed (1st method)
avso = [0] * 128  # average speed (2nd method)
av_c = [0] * 128  # running count used to calculate the average speeds

# Split data into lists for easy use
for i in range(0, len(datl)):
    splt = datl[i].split(",", 5)
    t[i] = float(splt[0])
    rc[i] = float(splt[1])
    so[i] = float(splt[2])
    hval[i] = float(splt[4])
    pval[i] = int(splt[5])
    
    if (i == 0):
        st[i] = 0
        dt[i] = 0
    else:
        st[i] = t[i] - t[0]
        dt[i] = t[i] - t[i - 1]

# Process data
for i in range(0, len(datl)):
    if hval[i] == 0:
        hval[i] = 2  # ADC ERROR
    elif hval[i] >= 612:
        hval[i] = 0  # High value
    else:
        hval[i] = 1  # Low Value
    avso[pval[i]] += so[i]
    av_c[pval[i]] += 1

# Calculate the average speed (from the live calculations on the pi)
for i in range(0, 128):  
    avso[i] = avso[i] / av_c[i]

# Calculate the speed after-the-fact (is the calculation going wrong? Unlikely.)
indx_last = 0
dt = 0
speed_cur = 0
for i in range(0, len(datl)):
    if (st[i] - st[indx_last]) >= 0.01:  # if 0.1s has passed...
        dt = st[i] - st[indx_last]
        speed_cur = ((rc[i] - rc[indx_last]) / dt) * 60 # ((dMag * Rev/Mag) / dt), Rev/Mag = 1
        indx_last = i
    s[i] = speed_cur
    avs[pval[i]] += s[i]

# Calculate the average after-the-fact speed
for i in range(0, 128):
    avs[i] = avs[i] / av_c[i]

ssm = [0] * 100
sosm = [0] * 100
step = len(datl) / 100

for i in range(0, 100):
    ssm[i] = s[i * step]
    sosm[i] = so[i * step]

# Plot Data
f = plt.figure(figsize=(15, 15))
ax1 = f.add_subplot(111)
ax1.set_autoscale_on(False)
ax1.plot(st[-200:], hval[-200:])
ax1.axis([638.5, 641, -0.1, 1.1]) 
ax1.set_xlabel(r'Time, s', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'HES High or Low, digital', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./HES_Waveform.png")

# Plot Data
f = plt.figure(figsize=(15, 15))
ax1 = f.add_subplot(111)
ax1.plot(range(0, 128), avso, 'b')
ax1.plot(range(0, 128), avs, 'r')
ax1.set_xlabel(r'Potentiometer Value, unitless', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'Average Speed, RPM', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./HES_Speed_test.png")

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
