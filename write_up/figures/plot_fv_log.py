import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import glob

import pandas as pd
from plothelp import fit_line

def fitf(x, a, b):
    return a * x[0] + b + 0.0156 * x[1]

def fit2f(x, a, b, c):
    return a * np.log(x[0]) + c

if False:
    # Geometry of the couette cell

    roo = 0.044151 / 2.0  # outer cell outer radius in m
    ro = 0.039111 / 2.0  # outer cell radius in m
    ri = 0.01525  # inner cell radius in m

    icxsa = np.pi * (ri ** 2)
    ocxsa = np.pi * (ro ** 2)
    dxsa = ocxsa - icxsa  # vol per height in m3/m
    dxsa = dxsa * 1000 # l / m
    dxsa = dxsa * 1000 # ml / m

    fill_height = 15 / dxsa

    # Reads the data
    datf = pd.read_csv("./../../logs/g9873c.csv")

    stg     = datf['t']
    stg     = stg - stg[0]
    dr      = datf['dr']
    cr      = datf['cr']
    cr2a    = datf['cr2a']
    cr2b    = datf['cr2b']
    pv      = datf['pv']

    # Filter noise from data
    dr = filter(stg, dr, method="butter", A=2, B=0.0001)
    cr = filter(stg, cr, method="butter", A=2, B=0.0001)
    cr2a = filter(stg, cr2a, method="butter", A=2, B=0.0001)
    cr2b = filter(stg, cr2b, method="butter", A=2, B=0.0001)

    # Chop off unwanted data
    start   = 20000
    stop    = -1 * (int(len(cr) * 1) - 25000)
    skip    = 1000
    stg     = stg[start:stop:skip]
    dr      = dr[start:stop:skip]
    cr      = cr[start:stop:skip]
    cr2a    = cr2a[start:stop:skip]
    cr2b    = cr2b[start:stop:skip]
    pv      = pv[start:stop:skip]

    # Calculate the required stall torque for these readings
    musg    = [1.129] * len(cr)
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    gam_dot = (sp_rads * ri) / (ro - ri)
    tau     = musg * gam_dot
    T       = tau * (2 * np.pi * ri * ri * fill_height) 

    Ts      = T / (1.0 - (sp_rpms / sn_rpms))
    cu      = 16.573 * cr - 29.778
    cu2a    = 11.307 * cr2a - 29.066
    cu2b    = 11.307 * cr2b - 29.066
    cub     = 0.00229473 * pv + 0.48960784
    cu      = (cu + cu2a + cu2b) / 3
    vo      = 0.0636 * pv + 2.423

    # Relate the stall torque to the current supply
    eff, __ =  curve_fit(fit2f, [(cu - cub)], T)
    

    # Calculate the viscosity using the read data and the fit #####################################################################################################################################
    Tg_fc       = eff[0] * np.log((cu - cub)) + eff[2]
    taug_fc     = Tg_fc / (2 * np.pi * ri * ri * fill_height)
    mug_fc = taug_fc / gam_dot

    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    ax.errorbar((cu - cub), T, xerr=(0.05 * np.array(cu)), marker='o', linestyle='None', label="$Required\ Torque$")
    ax.plot((cu-cub), ((cu - cub) * eff[0] + eff[1]), label="$T\ =\ {:.3E} * \Delta I_{} + {:.3E}$".format(eff[0], "{ms}", eff[1]))

    ax.set_xlabel("\n $\Delta Current,\ A$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Torque,\ Nm$\n", ha='center', va='center', fontsize=24)
    #plt.legend(loc=4)
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_t_cal_log.png")

def check(filename, viscosity, fillvol):
    ########### Check the calibration using the water run
    # Reads the data

    # Geometry of the couette cell

    roo = 0.044151 / 2.0  # outer cell outer radius in m
    ro = 0.039111 / 2.0  # outer cell radius in m
    ri = 0.01525  # inner cell radius in m

    icxsa = np.pi * (ri ** 2)
    ocxsa = np.pi * (ro ** 2)
    dxsa = ocxsa - icxsa  # vol per height in m3/m
    dxsa = dxsa * 1000 # l / m
    dxsa = dxsa * 1000 # ml / m

    fill_height = fillvol / dxsa

    datf = pd.read_csv(filename)

    stw     = datf['t']
    stw     = stw - stw[0]
    dr      = datf['dr']
    cr      = datf['cr']
    cr2a    = datf['cr2a']
    cr2b    = datf['cr2b']
    pv      = datf['pv']

    # Filter noise from data
    dr      = filter(stw, dr, method="butter", A=2, B=0.001)
    cr      = filter(stw, cr, method="butter", A=2, B=0.001)
    cr2a    = filter(stw, cr2a, method="butter", A=2, B=0.001)
    cr2b    = filter(stw, cr2b, method="butter", A=2, B=0.001)

    # Calculate viscosity
    musw    = [viscosity] * len(cr)
    cu      = 16.573 * cr - 29.778
    cu2a    = 11.307 * cr2a - 29.066
    cu2b    = 11.307 * cr2b - 29.066
    cu      = np.array((cu + cu2a + cu2b) / 3)
    cub     = 0.00229473 * pv + 0.48960784
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    vo      = 0.0636 * pv + 2.423

    #T calibration
    gam_dotw    = (sp_rads * ri) / (ro - ri)
    #Tw_fc       = eff[0] * (cu - cub) + eff[1] ##########################################################################################################################################################################################################################################################################
    Tw_fc       = eff[0] * np.log(np.abs(cu - cub)) + eff[2]
    tauw_fc     = Tw_fc / (2 * np.pi * ri * ri * fill_height) 
    muw_fc = tauw_fc / gam_dotw
    return stw, muw_fc, musw

def calc_mu(sp_rpms, cu, pv, eff, fill_volume):
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

    # Calculate viscosity
    cub     = 0.00229473 * pv + 0.48960784
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    vo      = 0.0636 * pv + 2.423
    gam_dot = (sp_rads * ri) / (ro - ri)
    T       = (eff[0] * (cu - cub) + eff[1])
    #T       = Ts * (1 - (sp_rpms / sn_rpms))
    tau     = T / (2 * np.pi * ri * ri * fill_height) 
    mu      = tau / gam_dot
    return mu

def get_reqt(filename, viscosity, fill_volume):
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

    stg     = np.array(datf['t'])
    stg     = stg - stg[0]
    dr      = np.array(datf['dr'])
    cr      = np.array(datf['cr'])
    cr2a    = np.array(datf['cr2a'])
    cr2b    = np.array(datf['cr2b'])
    pv      = np.array(datf['pv'])

    # Filter noise from data
    dr = filter(stg, dr, method="butter", A=2, B=0.0001)
    cr = filter(stg, cr, method="butter", A=2, B=0.0001)
    cr2a = filter(stg, cr2a, method="butter", A=2, B=0.0001)
    cr2b = filter(stg, cr2b, method="butter", A=2, B=0.0001)

    # Chop off unwanted data
    start   = 20000
    stop    = -1 * (int(len(cr) * 1) - 25000)
    skip    = 1000
    stg     = stg[start:stop:skip]
    dr      = dr[start:stop:skip]
    cr      = cr[start:stop:skip]
    cr2a    = cr2a[start:stop:skip]
    cr2b    = cr2b[start:stop:skip]
    pv      = pv[start:stop:skip]

    # Calculate the required stall torque for these readings
    musg    = [viscosity] * len(cr)
    sp_rpms = dr * 308.768 - 167.08
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    gam_dot = (sp_rads * ri) / (ro - ri)
    tau     = musg * gam_dot
    T       = tau * (2 * np.pi * ri * ri * fill_height) 
    snns    = sp_rpms / sn_rpms
    Ts      = T / (1 - (snns))
    for i in range(0, len(snns)):
        if snns[i] > 1:
            Ts[i] = 0
    cu      = 16.573 * cr - 29.778
    cu2a    = 11.307 * cr2a - 29.066
    cu2b    = 11.307 * cr2b - 29.066
    cub     = 0.00229473 * pv + 0.48960784
    cu      = (cu + cu2a + cu2b) / 3
    return cu, cub, T, musg, sp_rpms, pv, gam_dot
    
if False:
    st9873, mufc9873, mus9873, sp_rpms9873, pv9873 = check("./../../logs/g9873c.csv", 1.129, 15)
    st9623, mufc9623, mus9623, sp_rpms9623, pv9623 = check("./../../logs/g9623c.csv", 0.9061, 15)
    st9375, mufc9375, mus9375, sp_rpms9375, pv9375 = check("./../../logs/g9375c.csv", 0.6102, 15)
    st8887, mufc8887, mus8887, sp_rpms8887, pv8887 = check("./../../logs/g8887c.csv", 0.4005, 15)

    # Plot
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    start = 20000
    stop = -1 * (len(st9873) - 115000)
    skip = 1000
    ax.plot(stg, musg, 'b')
    ax.plot(stg, mug_fc, 'bx')

    ax.plot(st9375[start:stop:skip], mus9375[start:stop:skip], 'g')
    ax.plot(st9375[start:stop:skip], mufc9375[start:stop:skip], 'g^')

    ax.plot(st9623[start:stop:skip], mus9623[start:stop:skip], 'r')
    ax.plot(st9623[start:stop:skip], mufc9623[start:stop:skip], 'r^')
    #ax.set_yscale('log')
    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_t_check_log.png")
else:
    cu9873, cub9873, Ts9873, mus9873, sp_rpms9873, pv9873, gd9873 = get_reqt("./../../logs/g9873c.csv", 1.129, 15)
    cu9623, cub9623, Ts9623, mus9623, sp_rpms9623, pv9623, gd9623 = get_reqt("./../../logs/g9623c.csv", 0.9061, 15)
    cu9375, cub9375, Ts9375, mus9375, sp_rpms9375, pv9375, gd9375 = get_reqt("./../../logs/g9375c.csv", 0.6102, 15)
    cu8887, cub8887, Ts8887, mus8887, sp_rpms8887, pv8887, gd8887 = get_reqt("./../../logs/g8887c.csv", 0.4005, 15)

    cus = np.array([np.average(cu9873 - cub9873), np.average(cu9623 - cub9623), np.average(cu9375 - cub9375), np.average(cu8887 - cub8887)])
    custd = [np.std(cu9873 - cub9873), np.std(cu9623 - cub9623), np.std(cu9375 - cub9375), np.std(cu8887 - cub8887)]
    
    mus = [np.average(mus9873), np.average(mus9623), np.average(mus9375), np.average(mus8887)]
    mustd = [np.std(mus9873), np.std(mus9623), np.std(mus9375), np.std(mus8887)]
    
    Tss = [np.average(Ts9873), np.average(Ts9623), np.average(Ts9375), np.average(Ts8887)]
    Tstd = [np.std(Ts9873), np.std(Ts9623), np.std(Ts9375), np.std(Ts8887)]
    
    cuf = cus
    Tsf = Tss
    
    cuf = [cus[0], cus[1], cus[3]]
    Tsf = [Tss[0], Tss[2], Tss[3]]
    
    outp, fiteqn, eff = fit_line(cuf, Tsf, 1, x_name="I_{ms}", y_name="T")

    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    ax.errorbar(cus, Tss, xerr=custd, yerr=Tstd, marker='o', linestyle='None', label="Calulated Torque")
    ax.plot(cuf, outp, label=fiteqn)
    ax.set_xlabel("\n $Current,\ A$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Torque,\ N.m$\n", ha='center', va='center', fontsize=24)
    plt.legend(loc=2)
    plt.savefig("./fig_t_ref_cal.png")
    plt.close(f)
    
    sp_rpms_sp = 5.13 * pv9873[0] + 15.275
    sp_rads_sp = 1
    gam_dot_sp = (((5.13 * 48 + 15.275) * 2 * np.pi) / 60 * 0.01525) / ((0.039111 / 2.0) - 0.01525)
    
    # Use calibration to calculate the viscosity of each solution
    muc9873 = calc_mu(sp_rpms9873, cu9873, pv9873, eff, 15)
    muc9623 = calc_mu(sp_rpms9623, cu9623, pv9623, eff, 15)
    muc9375 = calc_mu(sp_rpms9375, cu9375, pv9375, eff, 15)
    muc8887 = calc_mu(sp_rpms8887, cu8887, pv8887, eff, 15)
    
    mum9873 = np.average(muc9873)
    mum9623 = np.average(muc9623)
    mum9375 = np.average(muc9375)
    mum8887 = np.average(muc8887)
    
    mud9873 = np.std(muc9873)
    mud9623 = np.std(muc9623)
    mud9375 = np.std(muc9375)
    mud8887 = np.std(muc8887)

    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    ax.plot(gd9873, mus9873, 'b.')
    ax.plot(gd9623, mus9623, 'g.')
    ax.plot(gd9375, mus9375, 'r.')
    ax.plot(gd8887, mus8887, 'c.')
    
    ax.errorbar(np.average(gd9873), mum9873, xerr=np.std(gd9873), yerr=mud9873, linestyle='None', marker='o')
    ax.errorbar(np.average(gd9623), mum9623, xerr=np.std(gd9623), yerr=mud9623, linestyle='None', marker='o')
    ax.errorbar(np.average(gd9375), mum9375, xerr=np.std(gd9375), yerr=mud9375, linestyle='None', marker='o')
    ax.errorbar(np.average(gd8887), mum8887, xerr=np.std(gd8887), yerr=mud8887, linestyle='None', marker='o')
    ax.axvline(gam_dot_sp, linestyle='--', marker='None', color='y')
    
    #ax.set_yscale('log')
    ax.set_xlabel("\n $Strain\ Rate,\ s^{-1}$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)
    plt.savefig("./fig_t_ref_check.png")
