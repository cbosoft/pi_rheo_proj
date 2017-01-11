import matplotlib.pyplot as plt
import numpy as np
#data read from figure 6 {figshearthin}
x1 = [10000, 25000, 31000, 40000, 50000, 70000, 88000, 100000, 130000, 160000, 200000, 250000, 300000]
y1 = [3800, 2900, 2600, 2200, 1900, 1400, 1050, 780, 550, 400, 280, 195, 45]

#data read from figure on second page {figshearthick}
x2 = [0.0015, 0.02, 0.15, 0.45, 1.5, 11, 250, 1000, 4000, 10000, 20000]
y2 = [0.12, 0.12, 0.1, 0.05, 0.02, 0.018, 0.018, 0.02, 0.03, 0.03, 0.03]

f, (ax1, ax2) = plt.subplots(2)
#plt.suptitle('Shear Stress (Pa) vs Viscosity (Pa.s)')

#plot 1
ax1.set_title("Shear Thinning")
ax1.plot(x1, y1)
ax1.set_xscale("log")
ax1.set_yscale("log")
#plot 2
ax2.set_title("Shear Thickening")
ax2.plot(x2, y2)
ax2.set_xscale("log")
ax2.set_yscale("log")

# Set common labels
f.text(0.5, 0.04, 'Shear Stress (Pa)', ha='center', va='center')
f.text(0.06, 0.5, 'Viscosity (Pa.s)', ha='center', va='center', rotation='vertical')
plt.savefig("foo.png")

