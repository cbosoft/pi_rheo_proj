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
#from matplotlib import use as mpluse
#mpluse('Agg')  # can't remember this is here... fixes a bug perhaps?
import matplotlib.pyplot as plt

# RPi-R
sys.path.append("./../bin")
from plothelp import read_logf
from plothelp import fit_line
from filter import filter as filt_r
import resx

#log_files = ["../logs/ccal_09.10.17-0944.csv"]  # 
log_files = sorted(glob("./../logs/mcal_[123]*_11.10.17-1*.csv"))
#log_files = ["./../bin/test.csv"] * 1

########################################################################################################################
########################################################################################################################
## CALIBRATE

ln = "../logs/ccal_09.10.17-0944.csv"

print "Processing..."
print "\tLog: {}".format(ln)
try:
    __, st, f_spd0, r_spd0, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, Tc, Vpz, Vms, __, __, tag = read_logf(ln)
except KeyError:
    #old version of logs
    print "Something went wrong..."
    exit()

i_off = 0
i = 0
# lose unusable data
for j in range(len(st)):
    i = j - i_off
    if f_spd0[i] == 0 or f_spd1[i] == 0 or f_spd2[i] == 0 or r_spd0[i] == 0 or r_spd1[i] == 0 or r_spd2[i] == 0 or \
        f_spd0[i] > 4000 or f_spd1[i] > 4000 or f_spd2[i] > 4000 or r_spd0[i] > 4000 or r_spd1[i] > 4000 or r_spd2[i] > 4000:
        st = np.delete(st, i)
        f_spd0 = np.delete(f_spd0, i)
        r_spd0 = np.delete(r_spd0, i)
        f_spd1 = np.delete(f_spd1, i)
        r_spd1 = np.delete(r_spd1, i)
        f_spd2 = np.delete(f_spd2, i)
        r_spd2 = np.delete(r_spd2, i)
        cra = np.delete(cra, i)
        crb = np.delete(crb, i)
        Tc = np.delete(Tc, i)
        Vpz = np.delete(Vpz, i)
        Vms = np.delete(Vms, i)
        i_off += 1
if (len(st)) < 9:
    print "Too few data points"
    exit()

# Energy balance method calculation
omega   = list()
for i in range(0, len(f_spd1)):
     omega.append((f_spd0[i] + r_spd0[i] + f_spd1[i] + r_spd1[i] + f_spd2[i] + r_spd2[i]) / 6.0)
omega   = np.array(omega, np.float64)
#omega   = (omega * 2.0 * np.pi) / 60.0

current = resx.get_current(cra)

# Filtering!
voltage = filt_r(st, Vms)
omega   = filt_r(st, omega)
current = filt_r(st, current)

# Resistance measurements - lots because paranoid
R = np.average([15.9, 13.6, 16.4, 13.0, 13.3, 13.6, 13.6, 14.7, 15.4, 13.7, 16.4, 13.5, 17.4, 17.0])

# From datasheet: https://www.neuhold-elektronik.at/datenblatt/N7029.pdf
## NO LOAD
Vms_noload_V = 3.0
omega_noload_rpm = 3500
ke = Vms_noload_V / omega_noload_rpm

## STALL
Vms_stall_V = 3.0
omega_stall_rpm = 0
Ims_stall_A = 0.39
T_stall_Nm = 0.00251
kt = (T_stall_Nm * R) / Vms_stall_V

## MAX EFFICIENCY
T_maxeff_Nm = 0.00048
Vms_maxeff_V = 3.0
omega_maxeff_rpm = 2830.0
Ims_maxeff_A = 0.093
alt_kt = (T_maxeff_Nm * R) / (Vms_maxeff_V - (ke * omega_maxeff_rpm))

tol = 0.005
if ((1 - tol) * kt < alt_kt) and ((1 + tol) * kt > alt_kt):
    print "Calculated characteristic coefficients (+/- {} %)".format(tol * 100)
    print "\tke:", ke
    print "\tkt:", kt
else:
    print "Could not accurately calculate the motor characteristics!"
    exit()

T = kt * current

fit, __, cal  = fit_line(omega, T, 2)
print cal

########################################################################################################################
########################################################################################################################
## CALCULATION



for ln in log_files:
    print "Processing..."
    print "\tLog: {}".format(ln)
    try:
        __, st, f_spd0, r_spd0, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, Tc, Vpz, Vms, __, __, tag = read_logf(ln)
    except KeyError:
        #old version of logs
        print "\tSkipping"
        continue
    
    i_off = 0
    i = 0
    # lose unusable data
    for j in range(len(st)):
        i = j - i_off
        if f_spd0[i] == 0 or f_spd1[i] == 0 or f_spd2[i] == 0 or r_spd0[i] == 0 or r_spd1[i] == 0 or r_spd2[i] == 0 or \
            f_spd0[i] > 4000 or f_spd1[i] > 4000 or f_spd2[i] > 4000 or r_spd0[i] > 4000 or r_spd1[i] > 4000 or r_spd2[i] > 4000:
            st = np.delete(st, i)
            f_spd0 = np.delete(f_spd0, i)
            r_spd0 = np.delete(r_spd0, i)
            f_spd1 = np.delete(f_spd1, i)
            r_spd1 = np.delete(r_spd1, i)
            f_spd2 = np.delete(f_spd2, i)
            r_spd2 = np.delete(r_spd2, i)
            cra = np.delete(cra, i)
            crb = np.delete(crb, i)
            Tc = np.delete(Tc, i)
            Vpz = np.delete(Vpz, i)
            Vms = np.delete(Vms, i)
            i_off += 1
    if (len(st)) < 9: continue
    # Energy balance method calculation
    omega   = list()
    for i in range(0, len(f_spd1)):
         omega.append((f_spd0[i] + r_spd0[i] + f_spd1[i] + r_spd1[i] + f_spd2[i] + r_spd2[i]) / 6.0)
    omega   = np.array(omega, np.float64)

    current = resx.get_current(cra)
    
    # Filtering!
    voltage = filt_r(st, Vms)
    omega   = filt_r(st, omega)
    current = filt_r(st, current)
    
    omega_rads   = (omega * 2.0 * np.pi) / 60.0
    
    ################################################################################
    # Strain rate. #################################################################
    
    gamma_dot = resx.get_strain(omega_rads)
    
    ################################################################################
    # Random Equation From a Website. ##############################################
    #
    #   * torque is proportional to current
    #       > T = kt * Ims
    #   * voltage is (current times resistance) plus (?) emf from the motor.
    #       > V = Ims * R + emf
    #   * emf is proportional to the rotational speed
    #       > emf = ke * omega
    #
    #   Putting this together:
    #       > V = (T*R/kt) + ke*omega
    #   At no-load, T = 0
    
    # Resistance measurements - lots because paranoid
    R = np.average([15.9, 13.6, 16.4, 13.0, 13.3, 13.6, 13.6, 14.7, 15.4, 13.7, 16.4, 13.5, 17.4, 17.0])
    
    # From datasheet: https://www.neuhold-elektronik.at/datenblatt/N7029.pdf
    
    ## NO LOAD
    Vms_noload_V = 3.0
    omega_noload_rpm = 3500
    ke = Vms_noload_V / omega_noload_rpm
    
    ## STALL
    Vms_stall_V = 3.0
    omega_stall_rpm = 0
    Ims_stall_A = 0.39
    T_stall_Nm = 0.00251
    kt = (T_stall_Nm * R) / Vms_stall_V
    
    ## MAX EFFICIENCY
    T_maxeff_Nm = 0.00048
    Vms_maxeff_V = 3.0
    omega_maxeff_rpm = 2830.0
    Ims_maxeff_A = 0.093
    alt_kt = (T_maxeff_Nm * R) / (Vms_maxeff_V - (ke * omega_maxeff_rpm))
    
    tol = 0.005
    if ((1 - tol) * kt < alt_kt) and ((1 + tol) * kt > alt_kt):
        print "Calculated characteristic coefficients (+/- {} %)".format(tol * 100)
        print "\tke:", ke
        print "\tkt:", kt
    else:
        print "Could not accurately calculate the motor characteristics!"
        exit()
    
    #cal = (3.26382223E-07, -4.49875507E-04, -5.99331695) # from log fit
    #cal = (1.17948961E-09,  -1.91668541E-06,   2.88339746E-03)
    
    # "Inertial energy loss" due to spinning the cylinder (accounting for extra mass over the datasheet
    T = [0.0] * len(omega)
    T_base = list()
    T_orig = kt * current
    for i in range(len(current)):
        #base = np.e ** (cal[0] * (omega[i] ** 2) - cal[1] * omega[i] - cal[2])
        base = (cal[0] * (omega[i] ** 2) + cal[1] * omega[i] + cal[2])
        T[i] = T_orig[i] - base
        T_base.append(base)
    T = np.array(T)
    T_base = np.array(T_base, np.float64)
    
    tau = resx.get_stress(T, 15)
    mu_refaw = tau / gamma_dot
    
    print "Average results:"
    print "\tT:",         np.average(T),          "Nm"            #   should be on the order of 1E-05 (or e-08?)
    print "\tomega:",     np.average(omega),      "rpm"           #   should be around 300
    print "\ttau:",       np.average(tau),        "Pa"            #   
    print "\tgamma_dot:", np.average(gamma_dot),  "s^-1"          #   
    print "\tmu:",        np.average(mu_refaw),   "Pa.s"          #   should be around 0.010146
    
    f = plt.figure()
    plt.ion()
    plt.suptitle(ln)
    
    ax = f.add_subplot(311) #RCX
    ax.plot(st, T)
    ax.plot(st, T_orig)
    ax.plot(st, T_base)
    plt.grid(axis="both")
    ax.set_ylabel("T/Nm")
    
    ax = f.add_subplot(312) #RCX
    ax.plot(st, omega)
    plt.grid(axis="both")
    ax.set_ylabel("omega/RPM")
    ax.set_xlabel("t/s")
    
    ax = f.add_subplot(313) #RCX
    ax.plot(st, mu_refaw)
    plt.grid(axis="both")
    #ax.set_ylim([0.0, 2])
    ax.set_ylabel("mu/Pa.s")
    ax.set_xlabel("I/A")
    
    plt.show()
r = raw_input("Press enter to quit")
