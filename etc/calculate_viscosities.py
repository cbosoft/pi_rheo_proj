#! /usr/bin/env python
'''
Adds missing viscosity data to log files.

Reads in any log files, calculates shear, strain and viscosity data, and writes to file.

Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# System
from glob import glob
from copy import copy
import sys

# 3rd Party
import numpy as np
import scipy as sp
from matplotlib import use as mpluse
mpluse('Agg')  # can't remember this is here... fixes a bug perhaps?
import matplotlib.pyplot as plt

# RPi-R
sys.path.append("./../bin")
from plothelp import read_logf
from filter import filter as filt_r
import resx

# for each log file...
#   read in all the data
#   calculate viscosity (efficiency method)
#   calculate viscosity (other method?)
#   add new data to log file

log_files = sorted(glob("./../logs/tmc*.csv"))

#log_files = ["./../bin/test.csv"] * 1

for ln in log_files:
    print "processing {}".format(ln)
    t, st, f_spd0, r_spd0, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, Tc, Vpz, Vms, __, __, tag = read_logf(ln)
    
    # Energy balance method calculation
    omega   = list()
    for i in range(0, len(f_spd1)):
         omega.append((f_spd1[i] + r_spd1[i] + f_spd2[i] + r_spd2[i]) / 4.0)
    omega   = np.array(omega, np.float64)
    omega   = (omega * 2.0 * np.pi) / 60.0

    current = resx.get_current(cra)
    voltage = Vms
    
    omega   = filt_r(st, omega)
    current = filt_r(st, current)
    
    ################################################################################
    # Strain rate. #################################################################
    
    gamma_dot = resx.get_strain(omega)
    
    ################################################################################
    # Energy balance. ##############################################################
    
    efficiency = 0.8 ## total guess. Not even slightly correct.
    tau       = (efficiency * current * voltage) / omega  
    mu_energy_balance_method = tau / gamma_dot
    
    ################################################################################
    # Current relation. ############################################################
    
    current_coil = resx.get_current_coil(voltage)
    T = resx.cal_TauIemf[0] * (current - current_coil) + resx.cal_TauIemf[1]
    tau    = resx.get_stress(T, 15)
    mu_current_relation = tau / gamma_dot
    
    ################################################################################
    # Updating log. ################################################################
    
    logf = open("{}_calcd.csv".format(ln[:-4]), "w")
    logf.write("t,f_spd0,r_spd0,f_spd1,r_spd1,f_spd2,r_spd2,cra,crb,T,Vpz,Vms,gamma_dot,tau,mu_en_bal,mu_current_relation\n")
    for i in range(0, len(t)):
        line = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                t[i], f_spd0[i], r_spd0[i], f_spd1[i], r_spd1[i], #5
                f_spd2[i], r_spd2[i], cra[i], crb[i], #4
                Tc[i], Vpz[i], voltage[i], gamma_dot[i], tau[i], #5
                mu_energy_balance_method[i], mu_current_relation[i]) #2
        logf.write(line)
    logf.close()
