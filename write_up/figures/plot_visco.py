import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
import numpy as np
import glob

import pandas as pd

# Read csv

def calc_v(filename, fill_volume=5):
    #log = "./../../logs/long_cal.csv"
    #datf = pd.read_csv(sorted(glob.glob("./../../logs/water_cal_10ml/*.csv"))[-1])
    datf = pd.read_csv(filename)

    # Cell geometry
    roo = 0.044151 / 2.0  # outer cell outer radius in m
    ro = 0.039111 / 2.0  # outer cell radius in m
    ri = 0.01525  # inner cell radius in m
    #L = 0.039753 - (roo - ro)  # height of couette cell

    icxsa = np.pi * (ri ** 2)
    ocxsa = np.pi * (ro ** 2)
    dxsa = ocxsa - icxsa  # vol per height in m3/m
    dxsa = dxsa * 1000 # l / m
    dxsa = dxsa * 1000 # ml / m

    fill_height = fill_volume / dxsa

    # Split up csv columns
    t = datf['t']
    st = t - t[0]
    dr = datf['dr']
    cr = datf['cr']
    pv = datf['pv']

    # Filtering: aye or naw?
    if True:
        dr = filter(st, dr, method="butter",A=2, B=0.001)
        cr = filter(st, cr, method="butter",A=2, B=0.001)

    # Calculate viscosity etc
    cu = cr * 3.58 - 7.784
    cu = cr * 0 + 0.5
    sp_rpms = dr * 312.809 - 159.196
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    Ts = (0.14 * cu + 0.032) * 0.1
    T = Ts * (1 - (sp_rpms / sn_rpms))
    tau = T / (2 * np.pi * ri * ri * fill_height)
    gam_dot = (sp_rads * ri) / (ro - ri)
    mu = tau / gam_dot

    # Again wi the filtering?
    if True:
        mu = filter(st, mu, method="butter", A=2, B=0.001)
    atot = 0
    for a in mu:
        atot += a
    muav = atot/len(mu)
    return st, sp_rpms, tau, gam_dot, mu, muav

if __name__=="__main__":
    st5, sp5, tau5, gam_dot5, mu5, av5 = calc_v(sorted(glob.glob("./../../logs/water_cal_5ml/*.csv"))[-1], 5)
    st10, sp10, tau10, gam_dot10, mu10, av10 = calc_v(sorted(glob.glob("./../../logs/water_cal_10ml/*.csv"))[-1], 10)
    
    print "10ml: {}\n5ml:  {}".format(av10, av5)
    # Set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    l = 85000
    h = -25000
    # Plot data and trendline
    ax.plot(st5[l:h], mu5[l:h], 'b-')
    ax.plot(st10[l:h], mu10[l:h], 'g-')

    #ax.set_ylim([-0.5, 0.5])
    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)

    # Show plot
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_visco_v_t_.png")
    plt.close(f)

    # Set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)

    # Plot data and trendline
    ax.plot(st5[l:h], sp5[l:h], 'b-')
    ax.plot(st10[l:h], sp10[l:h], 'g-')
    ax.set_xlabel("\n $Shear\ Stress,\ Pa$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)

    # Show plot
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_visco_v_tau_.png")

