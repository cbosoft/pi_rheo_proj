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
    vo      = 0.0636 * pv + 2.423
    pe      = cu * vo

    # Relate the stall torque to the current supply
    fit_ts, feqn, __ = fit_line(vo, T, 1, "V_{ms}", "Ts")
    eff, __ =  curve_fit(fitf, [cu, vo, gam_dot], T)
    fit_coeffs = [0.0156, -0.01218]

    # Calculate the viscosity using the read data and the fit
    #T = fit_coeffs[0] * cu + fit_coeffs[1]
    T = 0.0156 * cu + eff[-2] * vo + eff[-1] / gam_dot
    tau     = T / (2 * np.pi * ri * ri * fill_height)
    mu_calc = tau / gam_dot

    # Plot
    f = plt.figure()
    plt.title(viscosity)
    ax = f.add_subplot(111)
    ax.loglog(st, mus)
    ax.loglog(st, mu_calc)
    plt.grid(which='both', axis='both')
    plt.savefig(output)
    return eff#fit_coeffs

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
    dr      = filter(st, dr, method="butter", A=2, B=0.0001)
    cr      = filter(st, cr, method="butter", A=2, B=0.0001)
    
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
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    vo      = 0.0636 * pv + 2.423
    pe      = cu * vo
    
    #T calibration
    T       = 0.0156 * cu + eff[-2] * vo + eff[-1] / gam_dot
    tau     = T / (2 * np.pi * ri * ri * fill_height) 
    gam_dot = (sp_rads * ri) / (ro - ri)
    mu_calc = tau / gam_dot
    taur     = mus * gam_dot
    Tr       = taur * (2 * np.pi * ri * ri * fill_height) 

    # Plot
    f = plt.figure()
    ax = f.add_subplot(111)
    ax.loglog(st, mus)
    ax.loglog(st, mu_calc)
    plt.grid(which='both', axis='both')
    plt.savefig(output)

def fitf(x, b, c):
    return 0.0156 * x[0] + b * x[1] + c / x[2]

if __name__ == "__main__":
    f = cal_and_comp("./../../logs/water_long_sweep.csv", "./cal.png", 0.001005, 15)
    calc("./../../logs/glycerol_long_sweep.csv", "./check.png", 1.145, 15, f)
