import sys

sys.path.append("./../bin")

from filter import filter

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import glob

import pandas as pd
from plothelp import fit_line

# Import water and Glycerol data
datw    = pd.read_csv("./../../logs/dual_hes_long1000.csv")
st      = np.array(datw['t'])
st      = st - st[0]
cr      = np.array(datw['cr'])
cra     = np.array(datw['cr2a'])
crb     = np.array(datw['cr2b'])

f = plt.figure(figsize=(10, 10))
ax = f.add_subplot(111)

coeffs1 = [16.573, -29.778]
coeffs2 = [12.517, -32.246]

cu1 = coeffs1[0] * cr + coeffs1[1]
cu2 = coeffs2[0] * cra + coeffs2[1]
cu3 = coeffs2[0] * crb + coeffs2[1]

#ax.plot(st, cu1, color=(0, 0, 1, 0.15))
#ax.plot(st, cu2, color=(0, 1, 0, 0.15))
#ax.plot(st, cu3, color=(1, 0, 0, 0.15))

cu1 = filter(st, cu1, method="butter", A=2, B=0.001)
cu2 = filter(st, cu2, method="butter", A=2, B=0.001)
cu3 = filter(st, cu3, method="butter", A=2, B=0.001)

ax.plot(st, cu1, color=(0, 0, 1), label="30A HECS")
ax.plot(st, cu2, color=(0, 1, 0), label="5A HECS 1")
ax.plot(st, cu3, color=(1, 0, 0), label="5A HECS 2")

ax.set_ylim([0, 1])
ax.set_xlabel("\n $t,\ Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$I_{ms},\ Measured Current,\ A$\n", ha='center', va='center', fontsize=24)
plt.legend(loc=4)
plt.grid(which='both', axis='both')
plt.savefig("./fig_hecs_comp.png")





