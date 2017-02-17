# for every log file in params folder
# calculate the range of speeds for both algorithms
# param with the least variance is probably the best

import matplotlib.pyplot as plt
from glob import glob

#set up lists
total_one = [0] * 0
total_two = [0] * 0
count = [0] * 0
averages_one = [0] * 0
averages_two = [0] * 0
ranges_one = [0] * 0
ranges_two = [0] * 0
min_one = [0] * 0
min_two = [0] * 0
max_one = [0] * 0 # one is tick
max_two = [0] * 0 # two is span
temp_max_one = 0
temp_min_one = 1000000000
temp_max_two = 0
temp_min_two = 1000000000

#Read logfile
for s in sorted(glob("./paramscheck/*.csv")):
    datf = open(s, "r")
    datl = datf.readlines()

    temp_max_one = 0
    temp_min_one = 1000000000
    temp_max_two = 0
    temp_min_two = 1000000000

    speed_one = [0] * 0
    speed_two = [0] * 0

    total_one.append(0)
    total_two.append(0)
    count.append(0)
    averages_one.append(0)
    averages_two.append(0)
    ranges_one.append(0)
    ranges_two.append(0)

    for i in range(1, len(datl)):
        splt = datl[i].split(",", 5)
        # t[i] = float(splt[0])
        # rc[i] = float(splt[1])
        total_one[len(total_one) - 1] += float(splt[2])

        if float(splt[2]) > temp_max_one:
            temp_max_one = float(splt[2])
        if float(splt[2]) < temp_min_one:
            temp_min_one = float(splt[2])

        total_two[len(total_two) - 1] += float(splt[3])

        if float(splt[3]) > temp_max_two:
            temp_max_two = float(splt[3])
        if float(splt[3]) < temp_min_two:
            temp_min_two = float(splt[3])

        count[len(count) - 1] += 1
        # hval[i] = float(splt[4])
        # pval[i] = int(splt[5])

    min_one.append(temp_min_one)
    max_one.append(temp_max_one)
    min_two.append(temp_min_two)
    max_two.append(temp_max_two)

    datf.close()

# Calculate the averages and ranges
for i in range(0, len(count)):
    averages_one[i] = total_one[i] / count[i]
    averages_two[i] = total_two[i] / count[i]
    ranges_one[i] = max_one[i] - min_one[i]
    ranges_two[i] = max_two[i] - min_two[i]

# Plot Data
f = plt.figure(figsize=(15, 15))
ax1 = f.add_subplot(111)
ax1.plot(range(0, len(count)), averages_one, 'b')
ax1.plot(range(0, len(count)), averages_two, 'r')
ax1.set_xlabel(r'Tuning set', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'Average speed, RPM', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./params_speeds.png")

# Plot Data
f = plt.figure(figsize=(15, 15))
ax1 = f.add_subplot(111)
ax1.plot(range(0, len(count)), ranges_one, 'b')
ax1.plot(range(0, len(count)), ranges_two, 'r')
ax1.set_xlabel(r'Tuning set', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'Average speed, RPM', ha='center',
va='center', fontsize=12)

# Save the plot/show it
plt.savefig("./params_ranges.png")
