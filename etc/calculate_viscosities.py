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
from copy import copy

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

for ln in log_files:
    print "Processing..."
    print "\t{}".format(ln)
    
    __, st, __, omega_rads, __, __, __, __, Ims, __, __, __, Vms, __, __, __ = read_logf(ln, dia=True)
    gamma_dot, T, tau, mu = resx.calc_mu(st, Vms, Ims, 15, omega_rads)
    
    print "\n\tAverage results:"
    print "\tT:",         np.average(T),          "Nm"            #   should be on the order of 1E-05 (or e-08?)
    print "\tomega:",     np.average(omega_rads),      "rpm"           #   should be around 300
    print "\ttau:",       np.average(tau),        "Pa"            #   
    print "\tgamma_dot:", np.average(gamma_dot),  "s^-1"          #   
    print "\tmu:",        np.average(mu),   "Pa.s"          #   should be around 0.010146
    
    f = plt.figure()
    plt.ion()
    plt.suptitle(ln)
    
    ax = f.add_subplot(311) #RCX
    #ax.plot(st, domegadt)
    ax.plot(st, T, label="refab_method")
    plt.grid(axis="both")
    plt.legend()
    ax.set_ylabel("T/Nm")
    
    ax = f.add_subplot(312) #RCX
    ax.plot(st, omega_rads, label="omega, duh")
    plt.grid(axis="both")
    plt.legend()
    ax.set_ylabel("omega/(rad/s)")
    #ax.set_xlabel("t/s")
    
    ax = f.add_subplot(313) #RCX
    ax.plot(st, mu, label="mu_refab, av:{}".format(np.average(mu)))
    plt.grid(axis="both")
    plt.legend()
    #ax.set_ylim([0.0, 2])
    ax.set_ylabel("mu/Pa.s")
    ax.set_xlabel("t/s")
    
    plt.show()
r = raw_input("Press enter to quit")
