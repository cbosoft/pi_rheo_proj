#! /usr/bin/env python
'''
Adds missing viscosity data to log files.

Reads in any log files, calculates shear, strain and viscosity data, and writes to file.

Author: Chris Boyle (christopher.boyle.101@strath.ac.uk
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

log_files = sorted(glob("./../logs/rheometry*.csv"))


for log in log_files:
    print "processing {}".format(log)
    t, st, dr, cr, cr2a, cr2b, pv, T, Vpz, __, __, tag = ph.read_logf(log)
    
    # Energy balance method calculation
    omega   = resx.get_speed_rads(dr)
    current = resx.get_current(cr, cr2a, cr2b)
    voltage = resx.get_supply_voltage(pv)
    
    omega   = filt_r(st, omega)
    current = filt_r(st, omega)
    
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
    
    current_coil = resx.get_current_coil(pv)
    tau = resx.cal_K_tau_Ico[0] * (current - current_coil) + resx.cal_K_tau_Ico[1]
    mu_current_relation = tau / gamma_dot
    
    logf = open(log, "w")
    logf.write("t,dr,cr,cr2a,cr2b,pv,T,Vpz,gamma_dot,tau,mu_en_bal,mu_current_relation\n")
    for i in range(0, len(t)):
        line = "{},{},{},{},{},{},{},{},{},{},{},{}\n".format(t[i], dr[i], cr[i], cr2a[i], cr2b[i], pv[i], T[i], Vpz[i], gamma_dot[i], tau[i], mu_energy_balance_method[i], mu_current_relation[i])
        logf.write(line)
    logf.close()
