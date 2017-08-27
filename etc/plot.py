#! /usr/bin/env python
'''
Simple reading sorting and plotting of data logged from the RPi-R.

Reads data from any log files that are present and sorts by composition of cornstarch.
Plots a few simple checks and then plots shear stresses v strain rates.

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
from filter import filter as ft
import resx

#############################################################################################################
### Setting up. #############################################################################################
# Before the plot can begin, there are a few things to do first: setting up variables, reading the files etc.

# Change plotter font to serif, I think it looks nicer than sans fonts.
plt.rc('font', family='serif')

# The default font size is a bit titchy, so making it a bigger here.
font_size = 24

# Find the relevant log files, store them in an array
log_files = sorted(glob("./../logs/rheometry_test_*.csv"))

# Create dictionaries to store data from log files...
# Dictionaries are quick ways to store information using a "key" (the bit in the square brackets).
# This means we can sort the data by the run parameters -- the tags

Xs = dict()                             # Xs: X axis data, the time in seconds since the run began.
Xs["10wtpd0"] = np.array([], np.float64)  
Xs["20wtpd0"] = np.array([], np.float64)  
Xs["30wtpd0"] = np.array([], np.float64)  
Xs["40wtpd0"] = np.array([], np.float64)  
Xs["50wtpd0"] = np.array([], np.float64)  

Ys = dict()                             # Ys: Y axis data, the piezo voltages.
Ys["10wtpd0"] = np.array([], np.float64)  
Ys["20wtpd0"] = np.array([], np.float64)  
Ys["30wtpd0"] = np.array([], np.float64)  
Ys["40wtpd0"] = np.array([], np.float64)  
Ys["50wtpd0"] = np.array([], np.float64)  

DRs = dict()                             # DRs: Y axis data, speed of rotation
DRs["10wtpd0"] = np.array([], np.float64)  
DRs["20wtpd0"] = np.array([], np.float64)  
DRs["30wtpd0"] = np.array([], np.float64)  
DRs["40wtpd0"] = np.array([], np.float64)  
DRs["50wtpd0"] = np.array([], np.float64)

TAUs = dict()
TAUs["10wtpd0"] = np.array([], np.float64)  
TAUs["20wtpd0"] = np.array([], np.float64)  
TAUs["30wtpd0"] = np.array([], np.float64)  
TAUs["40wtpd0"] = np.array([], np.float64)  
TAUs["50wtpd0"] = np.array([], np.float64)

GDs = dict()
GDs["10wtpd0"] = np.array([], np.float64)  
GDs["20wtpd0"] = np.array([], np.float64)  
GDs["30wtpd0"] = np.array([], np.float64)  
GDs["40wtpd0"] = np.array([], np.float64)  
GDs["50wtpd0"] = np.array([], np.float64)


ADs = dict()                               # ADs: The antiderivative of the Y data.
ADs["10wtpd0"] = np.array([], np.float64)  # Y data is thought to be related to the 
ADs["20wtpd0"] = np.array([], np.float64)  # derivative of the drag force applied to the
ADs["30wtpd0"] = np.array([], np.float64)  # needle. The antiderivative taken here, if
ADs["40wtpd0"] = np.array([], np.float64)  # that is the case, should be directly related
ADs["50wtpd0"] = np.array([], np.float64)  # to the drag and therefore the viscosity of 
                                           # the fluid (and other things...)

## Set it so that these colours refer to logs with these tags...
colours = dict()
colours["10wtpd0"] = [0, 0, 1, 1]       # all plots of 10wt% runs are in blue
colours["20wtpd0"] = [0, 1, 0, 1]       # all plots of 20wt% runs are in green
colours["30wtpd0"] = [1, 0, 0, 1]       # all plots of 30wt% runs are in red
colours["40wtpd0"] = [1, 1, 0, 1]       # all plots of 40wt% runs are in yellow
colours["50wtpd0"] = [1, 0.5, 0.5, 1]   # all plots of 50wt% runs are in cyan

# set symbols for each wt% run
symbols = dict()
symbols["10wtpd0"] = "o"                # plots of 10wt% runs are in circles
symbols["20wtpd0"] = "^"                # plots of 20wt% runs are in triangles
symbols["30wtpd0"] = "8"                # plots of 30wt% runs are in more circles
symbols["40wtpd0"] = "D"                # plots of 40wt% runs are in diamonds
symbols["50wtpd0"] = "s"                # plots of 50wt% runs are in squares

# The list of tags we will be dealing with
tags = [
        "10wtpd0"
        , 
        "20wtpd0"
        , 
        "30wtpd0"
        , 
        "40wtpd0"
        , 
        "50wtpd0"
        ]

# The plot will skip some of the data points (as there are 1000s of them)
# This parameter defines how many to skip
# At the moment, the plot will only plot every 10th data point.
every = 1

# This is a quick function I wrote to sort of obtain the antiderivative of the signal..
# Hopefully this will show the something sensible!
# The piezo voltage should increase with viscosity of solution, and therefore the voltage
# displayed on the second plot should, on average, increase with increasing wt%.
def sort_of_discrete_antiderivative(x, y, sa=1):
    if sa < 2: sa = 2
    yo = sp.integrate.cumtrapz(y[:sa], x[:sa], initial=0)
    for i in range(sa, len(y)):
        yo = np.append(yo, sp.integrate.trapz(y[(i - sa):i], x[(i - sa):i]))
    return yo


#############################################################################################################
### Reading information from log files. #####################################################################
# For each file, open the spreadsheet and read the columns.
# Filter the piezo dataseries' and add save in the dictionarys set up earlier.

for f in log_files:
    __, st, dr, cr, cr2a, cr2b, pv, __, vraw, gd, tau, tag = ph.read_logf(f)
    
    print "Reading:    {}".format(f)
    #print "    gamma_dot: {}".format(np.average(gd))
    #print "    tau:       {}".format(np.average(tau))

    vfilc = ft(st, vraw)
    fdr = ft(st, dr)
    
    start = int(tag[:2])
    
    Xs[tag] = np.append(Xs[tag], st[start::every])
    Ys[tag] = np.append(Ys[tag], vfilc[start::every])
    ADs[tag] = np.append(ADs[tag], sort_of_discrete_antiderivative(st, vfilc)[start::every])
    DRs[tag] = np.append(DRs[tag], fdr[start::every])
    TAUs[tag] = np.append(TAUs[tag], tau[start::every])
    GDs[tag] = np.append(GDs[tag], gd[start::every])

#############################################################################################################
### First plot. #############################################################################################
# For each tag, plot data on figure, along with label information and specifc colour, marker for that wt%.

print "Plot:       piezo voltage v time"

plt.figure(figsize=(16, 16))
for t in tags:
    plt.plot(Xs[t], Ys[t], symbols[t], color=colours[t], label="{}%".format(t[:3]))
ax = plt.gca()
ax.set_xlabel("Time, s", fontsize=font_size)
ax.set_ylabel("Piezo signal, V ($\propto$ Derivative of Needle Drag Force)", fontsize=font_size)
plt.legend(loc=3)
plt.savefig("./../plots/logs_piezo_compare.png")

#############################################################################################################
### Second plot. ############################################################################################
# Sames as before, but with antiderivative data instead.

print "Plot:       antiderivative of piezo signal v time"

plt.figure(figsize=(16, 16))
for t in tags:
    plt.plot(Xs[t], ADs[t], symbols[t], color=colours[t], label="{}%".format(t[:3]))
ax = plt.gca()
ax.set_xlabel("Time, s", fontsize=font_size)
ax.set_ylabel("Piezo Voltage Antiderivative ($\propto$ Needle Drag, N)", fontsize=font_size)
plt.legend(loc=3)
plt.savefig("./../plots/logs_piezo_compare_antiderivatives.png")

#############################################################################################################
### Third plot. #############################################################################################
# Plot the filtered dynamo readings

print "Plot:       dynamo reading v time"

plt.figure(figsize=(16, 16))
for t in tags:
    plt.plot(Xs[t], DRs[t], symbols[t], color=colours[t], label="{}%".format(t[:3]))
ax = plt.gca()
ax.set_xlabel("Time, s", fontsize=font_size)
ax.set_ylabel("Dynamo Reading, V", fontsize=font_size)
plt.legend(loc=3)
plt.savefig("./../plots/logs_piezo_compare_speeds.png")

#############################################################################################################
### Fourth plot. ############################################################################################
# Plot normalised piezo readings

print "Plot:       antiderivative of piezo signal normalised by dynamo signal v time"

plt.figure(figsize=(16, 16))
for t in tags:
    normd = ADs[t] / DRs[t]
    plt.plot(Xs[t], normd, symbols[t], color=colours[t], label="{}%".format(t[:3]))
ax = plt.gca()
ax.set_xlabel("Time, s", fontsize=font_size)
ax.set_ylabel("\"normalised\" piezo reading", fontsize=font_size)
plt.legend(loc=3)
plt.savefig("./../plots/logs_piezo_compare_normalised.png")

#############################################################################################################
### Fifth plot. #############################################################################################
# Plot tau as function of gd

print "Plot:       shear stress v strain rate"

plt.figure(figsize=(16, 16))
for t in tags:
    #plt.plot(GDs[t], TAUs[t], symbols[t], color=colours[t], label="{}%".format(t[:3]))
    plt.loglog(GDs[t], TAUs[t], symbols[t], color=colours[t], label="{}%".format(t[:3]))
ax = plt.gca()
ax.set_xlabel(r"$\rm\ Strain\ Rate\ [\dot\gamma],\ s^{-1}$", fontsize=font_size)
ax.set_ylabel(r"$\rm\ Shear\ Stress\ [\tau],\ Pa.s$", fontsize=font_size)
plt.legend(loc=3)
plt.savefig("./../plots/logs_tau_v_gd.png")
