import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import pandas as pd


mu = [0] * 0
gam_dot = [0] * 0

# Read csv
datf = pd.read_csv("./../../logs/ref_fluid_rheom_res/g100.csv")
mu.append(datf['mu'])
gam_dot.append(datf['gam_dot'])
datf = pd.read_csv("./../../logs/ref_fluid_rheom_res/g9887.csv")
mu.append(datf['mu'])
gam_dot.append(datf['gam_dot'])
datf = pd.read_csv("./../../logs/ref_fluid_rheom_res/g9623.csv")
mu.append(datf['mu'])
gam_dot.append(datf['gam_dot'])
datf = pd.read_csv("./../../logs/ref_fluid_rheom_res/g9375.csv")
mu.append(datf['mu'])
gam_dot.append(datf['gam_dot'])
datf = pd.read_csv("./../../logs/ref_fluid_rheom_res/g8887.csv")
mu.append(datf['mu'])
gam_dot.append(datf['gam_dot'])


# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

# Plot data
for i in range(0, len(mu)):
    ax.plot(gam_dot[i], mu[i], 'o', label="$Read\ Data$")

ax.set_ylim([0, 2])
ax.set_xlabel("\n $Shear\ Rate,\ s^{-1}$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)

# Show Legend
plt.legend(["100 vol%", "98.87 vol%", "96.23 vol%", "93.75 vol%", "88.87 vol%"], loc=1)

# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_lab_rheom_results.png")
plt.close(f)
