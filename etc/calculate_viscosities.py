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
import plothelp as ph
from filter import filter as filt_r
import resx

# for each log file...
#   read in all the data
#   calculate viscosity (efficiency method)
#   calculate viscosity (other method?)
#   add new data to log file

#log_files = sorted(glob("./../logs/rheometry*.csv"))

log_files = ["./../bin/test.csv"] * 1

for log in log_files:
    print "processing {}".format(log)
    t, st, f_spd0, r_spd0, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, T, Vpz, voltage, __, __, tag = ph.read_logf(log)
    
    # Energy balance method calculation
    omega   = list()
    for i in range(0, len(r_spd1)):
        #omega.append(np.average([r_spd0[i], f_spd0[i], r_spd1[i], f_spd1[i], r_spd2[i], f_spd2[i]]))
        omega.append((r_spd1[i] + f_spd1[i]) / 2.0)
    omega = np.array(omega, np.float64)
    print np.average(omega)
    current = resx.get_current(cra, crb)
    
    #omega   = filt_r(st, omega)
    current = filt_r(st, current)
    
    ################################################################################
    # Strain rate. #################################################################
    # Directly related to the rotational speed of the cylinder, assuming no wall-slip
    #
    # gamma_dot = omega * (inner_radius / (outer_radius - inner_radius))
    
    gamma_dot = omega * (resx.icor / (resx.ocir - resx.icor)) 
    
    ################################################################################
    # Energy balance. ##############################################################
    # power = omega * tau = efficiency * current * voltage 
    # .: tau = (efficiency * current * voltage) / omega
    efficiency = 0.8
    tau       = (efficiency * current * voltage) / omega  
    mu_energy_balance_method = tau / gamma_dot
    
    ################################################################################
    # Current relation. ############################################################
    # Torque (tau) is a function of current only. Some current is used purely by the
    # resistance in the coil. Most of the current is used creating the EMF which drives
    # The motor. Let these currents be termed Ico for the current used uselessly in the
    # coils and Iemf for the useful EMF producing current. Ims is the total current 
    # supplied to the motor.
    #
    # Ims = Ico + Iemf  --> Iemf = Ims - Ico
    # tau = Kti * Iemf
    #
    # .: tau = Kti * (Ims - Ico)
    
    current_coil = resx.get_current_coil(voltage)
    tau = resx.cal_TauIemf[0] * (current - current_coil) + resx.cal_TauIemf[1]
    mu_current_relation = tau / gamma_dot
    
    logf = open("{}_calcd.csv".format(log[:-4]), "w")
    logf.write("t,f_spd0,r_spd0,f_spd1,r_spd1,f_spd2,r_spd2,cra,crb,T,Vpz,Vms,gamma_dot,tau,mu_en_bal,mu_current_relation\n")
    for i in range(0, len(t)):
        line = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                t[i], f_spd0[i], r_spd0[i], f_spd1[i], r_spd1[i], #5
                f_spd2[i], r_spd2[i], cra[i], crb[i], #4
                T[i], Vpz[i], voltage[i], gamma_dot[i], tau[i], #5
                mu_energy_balance_method[i], mu_current_relation[i]) #2
        logf.write(line)
    logf.close()
