import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import glob

import pandas as pd
from plothelp import fit_line


def cal_and_comp(filename, output, viscosity, fill_volume):
    # Geometry of the couette cell
    roo = 0.044151 / 2.0  # outer cell outer radius in m
    ro = 0.039111 / 2.0  # outer cell radius in m
    ri = 0.01525  # inner cell radius in m

    icxsa = np.pi * (ri ** 2)
    ocxsa = np.pi * (ro ** 2)
    dxsa = ocxsa - icxsa  # vol per height in m3/m
    dxsa = dxsa * 1000 # l / m
    dxsa = dxsa * 1000 # ml / m

    fill_height = fill_volume / dxsa

    # Reads the data
    datf = pd.read_csv(filename)
    
    st = datf['t']
    st = st - st[0]
    dr = datf['dr']
    cr = datf['cr']
    pv = datf['pv']

    # Filter noise from data
    dr = filter(st, dr, method="butter", A=2, B=0.0001)
    cr = filter(st, cr, method="butter", A=2, B=0.0001)
    
    # Chop off unwanted data
    start = 200000
    stop = -1 #* (len(cr) - start - 180 * 1000)
    skip = 1
    st = st[start:stop:skip]
    dr = dr[start:stop:skip]
    cr = cr[start:stop:skip]
    pv = pv[start:stop:skip]
    
    # Calculate the required stall torque for these readings
    mus     = [viscosity] * len(cr)
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    gam_dot = (sp_rads * ri) / (ro - ri)
    tau     = mus * gam_dot
    T       = tau * (2 * np.pi * ri * ri * fill_height) 
    Ts      = T / (1.0 - (sp_rpms / sn_rpms))
    cu      = (25.177 * cr) - 45.264
    cub     = 0.00229473 * pv + 0.48960784
    vo      = 0.0636 * pv + 2.423
    pe      = cu * vo

    # Relate the stall torque to the current supply
    #fit_ts, feqn, __ = fit_line(vo, T, 1, "V_{ms}", "Ts")
    eff, __ =  curve_fit(fit2f, [(cu - cub), vo], T, p0=[1000, 0, 0])
    print eff
    # Calculate the viscosity using the read data and the fit
    #T       = eff[0] * vo + eff[1] + 0.0156 * cu
    T       = eff[0] * (cu - cub) + eff[1] + eff[2] * vo
    tau     = T / (2 * np.pi * ri * ri * fill_height)
    mu_calc = tau / gam_dot

    # Plot
    f = plt.figure()
    plt.title(viscosity)
    ax = f.add_subplot(111)
    ax.loglog(st, mus)
    ax.loglog(st, mu_calc)
    #ax.plot(gam_dot, tau)
    plt.grid(which='both', axis='both')
    plt.savefig(output)#cal.png
    return eff

def calc(filename, output, viscosity, fill_volume, eff):
    # Geometry of the couette cell
    roo     = 0.044151 / 2.0  # outer cell outer radius in m
    ro      = 0.039111 / 2.0  # outer cell radius in m
    ri      = 0.01525  # inner cell radius in m

    icxsa   = np.pi * (ri ** 2)
    ocxsa   = np.pi * (ro ** 2)
    dxsa    = ocxsa - icxsa  # vol per height in m3/m
    dxsa    = dxsa * 1000 # l / m
    dxsa    = dxsa * 1000 # ml / m

    fill_height = fill_volume / dxsa

    # Reads the data
    datf    = pd.read_csv(filename)
    
    st      = datf['t']
    st      = st - st[0]
    dr      = datf['dr']
    cr      = datf['cr']
    pv      = datf['pv']

    # Filter noise from data
    dr      = filter(st, dr, method="butter", A=2, B=0.001)
    cr      = filter(st, cr, method="butter", A=2, B=0.001)
    
    # Chop off unwanted data
    start   = 200000
    stop    = -1 #* (len(cr) - start - 180 * 1000)
    skip    = 1
    st      = st[start:stop:skip]
    dr      = dr[start:stop:skip]
    cr      = cr[start:stop:skip]
    pv      = pv[start:stop:skip]

    # Calculate viscosity
    mus     = [viscosity] * len(cr)
    cu      = (25.177 * cr) - 45.264
    cub     = 0.00229473 * pv + 0.48960784
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    vo      = 0.0636 * pv + 2.423
    pe      = cu * vo
    
    #T calibration
    gam_dot = (sp_rads * ri) / (ro - ri)
    #T       = eff[0] * vo + eff[1] + 0.0156 * cu
    T       = eff[0] * (cu - cub) + eff[1] + eff[2] * vo
    tau     = T / (2 * np.pi * ri * ri * fill_height) 
    mu_calc = tau / gam_dot
    
    # Compare with Lab Rheom
    mur = [0] * 0
    gam_dotr = [0] * 0

    # Read csv
    datf = pd.read_csv("./../../logs/ref_fluid_rheom_res/g100.csv")
    mur.append(datf['mu'])
    gam_dotr.append(datf['gam_dot'])
    # Plot
    f = plt.figure()
    ax = f.add_subplot(111)
    ax.loglog(st, mus)
    ax.loglog(st, mu_calc)
    #s2t = np.linspace(min(st), max(st), len(mur))
    #ax.loglog(s2t, mur, 'rx')
    #ax.plot(gam_dotr[0], (np.array(gam_dotr[0]) / np.array(mur[0])))
    #ax.plot(gam_dot, tau)
    ax.set_xlabel("\n $Shear\ Rate,\ s^{-1}$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Shear Stress,\ Pa$\n", ha='center', va='center', fontsize=24)
    plt.grid(which='both', axis='both')
    plt.savefig(output)#check.png

def fitf(x, a, b):
    return a * x[0] + b + 0.0156 * x[1]

def fit2f(x, a, b, c):
    return a * x[0] + b + c * x[1]
    
if __name__ == "__main__":
    f = cal_and_comp("./../../logs/glycerol_long_sweep.csv", "./cal.png", 1.328, 15)
    calc("./../../logs/water_long_sweep.csv", "./check.png", 0.001005, 15, f)
