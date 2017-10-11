from glob import glob

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#read from files
#f = glob("./*.csv")[-1]
f = "rheometry_test_timingtest_111017_0938.csv"
print f

of = pd.read_csv(f)
t = np.array(of['t'], np.float64)
dt = list()

for i in range(1, len(t)):
    dt.append(t[i] - t[i - 1])

print np.average(dt)

# create the figure
f = plt.figure()


ax = f.add_subplot(111) # number hundreds are number of rows, 
                             # tens are number of columns, and units 
                             # is plot number (???)
# plot stuff here
ax.hist(dt, bins=100, range=(0, 0.002))

plt.title("Histogram of logging intervals")
plt.xlabel("Interval Times, ms")
plt.ylabel("Occurences")

plt.show()
#plt.savefig("test.py")
