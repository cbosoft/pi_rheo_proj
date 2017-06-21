#
# Plot motor characteristic curve
#

import sys

sys.path.append('./../bin')

from filter import filter
import numpy as np
import matplotlib.pyplot as plt

f = plt.figure(figsize=(9, 9))
ax = f.add_subplot(111)

# three lines: efficiency vs T, I vs T, speed vs T

T2 = [0, 0.00211]
I2 = [0.017, 0.27]
O2 = [2900, 0]

ax.plot(T2, I2, 'b-')
ax2 = ax.twinx()
ax2.plot(T2, O2, 'r-')

ax.set_xlabel("\n $T,\ Torque,\ N\,m$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$I,\ Current,\ A$\n", ha='center', va='center', fontsize=24)
ax2.set_ylabel("$\omega,\ Speed,\ RPM$", ha='center', va='top', fontsize=24)
ax.set_xlim([0,T2[1]])
plt.grid(which='both', axis='both')
plt.savefig("./fig_mot_char_example.png")
plt.close(f)

f = plt.figure(figsize=(9, 9))
ax = f.add_subplot(111)

# three lines: efficiency vs T, I vs T, speed vs T

T2 = [0, 0.25]
I2 = [0.82, 4.5]
O2 = [670, 0]

ax.plot(T2, I2, 'b-')
ax2 = ax.twinx()
ax2.plot(T2, O2, 'r-')

ax.set_xlabel("\n $T,\ Torque,\ N\,m$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$I,\ Current,\ A$\n", ha='center', va='center', fontsize=24)
ax2.set_ylabel("$\omega,\ Speed,\ RPM$", ha='center', va='top', fontsize=24)
ax.set_xlim([0,T2[1]])
plt.grid(which='both', axis='both')
plt.savefig("./fig_mot_char_actual.png")
plt.close(f)
