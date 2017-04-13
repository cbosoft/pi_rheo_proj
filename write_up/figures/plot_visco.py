import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
import numpy as np
import glob

import pandas as pd
from plothelp import fit_line

# Read csv

def calc_v(filename, fill_volume=5):
    datf = pd.read_csv(filename)

    # Cell geometry
    roo = 0.044151 / 2.0  # outer cell outer radius in m
    ro = 0.039111 / 2.0  # outer cell radius in m
    ri = 0.01525  # inner cell radius in m

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
        dr = np.array(filter(st, dr, method="butter",A=2, B=0.001))
        cr = np.array(filter(st, cr, method="butter",A=2, B=0.001))
    for i in range(1, len(cr)):
        if cr[i] < 2.28: cr[i] = 2.3
        if cr[i] > 2.4: cr[i] = 2.4

    # Calculate viscosity etc
    cu      = (-956.06 * (cr ** 3)) + (6543.97 * (cr ** 2)) + (-14924.369 * cr) + 11341.612
    dr = dr *0.9
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    vo      = 0.0636 * pv + 2.423
    pe      = cu * vo
    #T       = (0.001640) * pe - 0.001835
    #Ts      = (0.173 * (cu**2)) + (-0.47 * cu) + 0.362
    Ts      = 41.75 * cu - 28.88
    T       = Ts * (1 - (sp_rpms / sn_rpms))
    tau     = T / (2 * np.pi * ri * ri * fill_height) 
    gam_dot = (sp_rads * ri) / (ro - ri)
    
    
    
    #holy moses, more filtering?
    if True:
        tau     = filter(st, tau, method="butter", A=2, B=0.001)
        #tau     = filter(st, tau, method="spline")
        gam_dot = filter(st, gam_dot, method="butter", A=4, B=0.001)
    
    mu = tau / (gam_dot)
    
    mu = mu
    
    # Again wi the filtering?
    if True:
        mu = filter(st, mu, method="butter", A=2, B=0.001)
    atot = 0
    for a in mu:
        atot += a
    muav = atot/len(mu)
    return st, sp_rpms, tau, gam_dot, mu, muav, cu, sn_rpms, pe, T

def calc_T(filename, fill_volume=5, visc=0.001):
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
        dr = np.array(filter(st, dr, method="butter",A=2, B=0.001))
        cr = np.array(filter(st, cr, method="butter",A=2, B=0.001))
    
    # Fix out of range current readings
    for i in range(1, len(cr)):
        if cr[i] < 2.28: cr[i] = 2.28
        if cr[i] > 2.4: cr[i] = 2.4
    cr = filter(st, cr, method="butter", A=2, B=0.0001)
    
    # Calculate torque
    mus     = [visc] * len(cr)
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    gam_dot = (sp_rads * ri) / (ro - ri)
    tau     = mus * gam_dot
    T       = tau * (2 * np.pi * ri * ri * fill_height) 
    Ts      = T / (1.0 - (sp_rpms / sn_rpms))
    cu      = (-956.06 * (cr ** 3)) + (6543.97 * (cr ** 2)) + (-14924.369 * cr) + 11341.612
    vo      = 0.0636 * pv + 2.423
    pe     = cu * vo
    return st, mus, sp_rpms, sp_rads, gam_dot, tau, T, cu, vo, pe, Ts, sn_rpms, pv

def cal_T(file, visco, fillvol, l, h):
    ## CALIBRATE TORQUE READINGS
    st, mus, sp_rpms, sp_rads, gam_dot, tau, T, cu, vo, pe, Ts, sn_rpms, pv = calc_T(file, fillvol, visco)

    x = cu[l:h]
    y = Ts[l:h]
    f, feqn, __ = fit_line(x, y, 1, "I_{ms}", "Ts")
    print feqn
    return x, y, f, feqn, sp_rpms[l:h], sn_rpms[l:h], pv[l:h]

if __name__=="__main__":
    l = 100000
    h = -1
    xg15, yg15, fg15, feqng15, sp_rpms15, sn_rpms15, pv15 = cal_T(sorted(glob.glob("./../../bin/test scripts/glyc_sweep_15ml/*.csv"))[-1], 1.141, 15, l, h)
    xw10, yw10, fw10, feqnw10, sp_rpms10, sn_rpms10, pv10 = cal_T(sorted(glob.glob("./../../logs/water_cal_10ml/*.csv"))[-1], 0.001005, 10, l, h)
    
    f = plt.figure(figsize=(16, 8))
    ax = f.add_subplot(121)

    # Plot data + fit (GLYCEROL)
    ax.plot(xg15, yg15, 'r.', label="$Glycerol\ 100\%,\ 15ml$")
    ax.plot(xg15, fg15, 'r--', label=feqng15)
    weight_cal_Ts15 = (0.173 * (xg15**2)) + (-0.47 * xg15) + 0.362
    weight_cal_T15 = (1 - (sp_rpms15 / sn_rpms15))
    ax.plot(xg15, weight_cal_T15, 'y--', label="$weight calibrated$")

    
    ylim = 20
    #ax.set_ylim([-ylim, ylim])
    ax.set_xlabel("\n $Supply\ Current,\ A$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Stall\ Torque,\ Nm$\n", ha='center', va='center', fontsize=24)

    plt.legend(loc=2)
    plt.grid(which='both', axis='both')

    ax2 = f.add_subplot(122)

    # Plot data + fit (WATER)
    ax2.plot(xw10, yw10, 'b.', label="$Water\ 100\%,\ 10ml$")
    ax2.plot(xw10, fw10, 'b--', label=feqnw10)

    #ax2.set_ylim([-(ylim / 20), ylim / 20])
    ax2.set_xlabel("\n $Supply\ Power,\ W$", ha='center', va='center', fontsize=24)
    ax2.set_ylabel("$Torque,\ Nm$\n", ha='center', va='center', fontsize=24)

    plt.legend(loc=2)
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_torque_cal.png")
    plt.close(f)
    
    ## CHECK CALIBRATION
    st, sp, tau, gam_dot, mu, av, cr, sn, pe, T = calc_v(sorted(glob.glob("./../../bin/test scripts/glyc_sweep_15ml/*.csv"))[-1], 15)
    #st, sp, tau, gam_dot, mu, av, cr, sn, pe, T = calc_v(sorted(glob.glob("./../../logs/water_cal_10ml/*.csv"))[-1], 15)
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    
    # Plot data
    ax.plot(gam_dot[l:h], tau[l:h])
    
    # Get fit line
    fit, fit_eqn, coeffs = fit_line(gam_dot[l:h], tau[l:h], 1, "gamma", "tau")
    
    # Plot fit line
    ax.plot(gam_dot[l:h], fit, 'g--', label="$Gradient = {:.7f}$".format(coeffs[0]))
    
    ax.set_xlabel("\n $Strain\ Rate,\ s^{-1}$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Shear\ Stress,\ Pa$\n", ha='center', va='center', fontsize=24)

    # Show plot
    plt.legend(loc=1)
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_gam_v_tau.png")
    plt.close(f)
    
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    
    # Plot data
    ax.plot(gam_dot[l:h], mu[l:h])
    
    ax.set_xlabel("\n $Strain\ Rate,\ s^{-1}$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)

    # Show plot
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_gam_v_mu.png")
    plt.close(f)
