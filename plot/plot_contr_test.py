#
# Plots the control test response
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
drf = filter(st, dr, method="butter", A=2, B=0.005)

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Plot
ax.plot(st, dr, color=(0,0,1,0.1))
ax.plot(st, drf, color=(0,0,1))
ax.set_xlabel("\n $t,\ Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$V_D,\ Dynamo\ Voltage,\ V$\n", ha='center', va='center', fontsize=24)

# Save plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_contr_test.png")
plt.close(f)
