#
#

import sys

sys.path.append('./../../bin')

from filter import filter
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Load data
datf = pd.read_csv("./../../logs/contr_test.csv")
st = np.array(datf['t'], np.float64)
st = st - float(st[0])
dr = np.array(datf['dr'], np.float64)
pv = np.array(datf['pv'], np.float64)
sp = (312.806 * dr) - 109.196
spf = filter(st, sp, method="butter", A=2, B=0.005)
drf = filter(st, dr, method="butter", A=2, B=0.005)

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Plot
if 1 == 2:
    ax.plot(st, sp, color=(0,0,1,0.1))
    ax.plot(st, spf, color=(0,0,1))
    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)
else:
    ax.plot(st, dr, color=(0,0,1,0.1))
    ax.plot(st, drf, color=(0,0,1))
    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Dynamo\ Voltage,\ V$\n", ha='center', va='center', fontsize=24)

# Save plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_contr_test.png")
plt.close(f)
