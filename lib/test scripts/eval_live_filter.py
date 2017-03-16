#
# Evalutation:: Simulates the gathering of live data and displays both the raw data and the filtered data on a live updating plot.
#

import sys
sys.path.append("./..")

import filter
import numpy as np
import matplotlib.pyplot as plt

live = True

# get some noisy data

logf = open("./../../logs/jam_test.csv", "r")
datl = logf.readlines()
logf.close()

# sort the data into columns
st = [0] * 0
rv = [0] * 0

splt = datl[1].split(",", 5)
tz = float(splt[0])

print "sorting data"
for i in range(2, len(datl) - 2):
    splt = datl[i].split(",", 5)
    rv.append(float(splt[1]))
    st.append(float(splt[0]) - tz)

# filter

fv = filter.filter(st, rv)

#prepare to plot
print "plotting"

if live:
    plt.ion()
else:
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)

delay = 100

for i in range(100, len(st) / 100):
    if not live:
        ax.plot(st[:i], rv[:i], color=(0.5, 0.5, 0.5))
        ax.plot(st[:(i - delay)], filter.filter(st[:i], rv[:i])[:-delay], 'b')
    else:
        plt.clf()
        plt.plot(st[:i], rv[:i], color=(0.5, 0.5, 0.5))
        plt.plot(st[:(i - delay)], filter.filter(st[:i], rv[:i])[:-delay], 'b')
        plt.pause(0.03)

    prog = int(i * 100 / (len(st)/ 100))
    sys.stdout.write(('\r[ {0} ] {1}%').format(str('#' * (prog / 2)) + str(' ' * (50 - (prog / 2))), prog))
    sys.stdout.flush()

if not live:
    print "displaying plot"
    plt.show()
else:
    while True:
        plt.pause(0.03)

