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

mu_av = [0] * 0
gam_dot_av = [0] * 0

len1 = len(mu[0]) / 3

yerrs = [0] * len(mu)


for j in range(0, len(mu)):
    yerro = [0] * 0
    gam_dot_av = [0] * 0
    mu_av = [0] * 0
    for i in range(0, len1):
        mut = 0
        gamt = 0
        mus = [mu[j][i], mu[j][(i + len1)], mu[j][(i + (2 * len1))]]
        gam_dots = [gam_dot[j][i], gam_dot[j][(i + len1)], gam_dot[j][(i + (2 * len1))]]

        for mui in mus:
            mut += mui
        for gam in gam_dots:
            gamt += gam

        mu_av.append(mut / 3)
        gam_dot_av.append(gamt / 3)

        highest_mu = max(mus)
        lowest_mu = min(mus)
        yerro.append(highest_mu - lowest_mu)
    gam_dot[j] = gam_dot_av
    mu[j] = mu_av
    yerrs[j] = yerro

# Set up figure
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)


   
# Plot data
for i in range(0, len(mu)):
    ax.errorbar(gam_dot[i], mu[i], xerr=0.0, yerr=yerrs[i], fmt='o', label="$Read\ Data$")

ax.set_ylim([0, 2])
ax.set_xlabel("\n $Shear\ Rate,\ s^{-1}$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)

# Show Legend
plt.legend(["100 vol%", "98.87 vol%", "96.23 vol%", "93.75 vol%", "88.87 vol%"], loc=1)

# Show plot
plt.grid(which='both', axis='both')
plt.savefig("./fig_lab_rheom_results.png")
plt.close(f)
