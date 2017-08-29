'''
    Plot-helper: useful functions for processing data.
    
    Contains functions to fit simple functions to data (fit_line()), to 
    read all information from a log file (read_logf()), and a function to
    simply plot the data from a given log (plot_logf()).
    
    Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# System
import math

# 3rd Party
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import use as mpluse
mpluse('Agg')  # for plotting from commandline (with no xserver or anything)
import matplotlib.pyplot as plt
import pandas as pd

# RPi-R
from filter import filter
import resx

def fit_line(x, y, dg, x_name="x", y_name="y"):
    '''
    plothelp.fit_line(x, y, dg, **kwargs)
    
    Fits a polynomial to a data series.
    
    Parameters:
        x       (list, float)       X data.
        y       (list, float)       Y data.
        dg      (integer)           Order of the polynomial function to fit.
    
    **kwargs:
        x_name  (string)            Symbol to use for the 'x' series, will be used to create 
                                    a string representation of the resulting polynomial. Default is x
        y_name  (string)            Symbol to use for the 'y' series, will be used to create 
                                    a string representation of the resulting polynomial. Default is y
    
    Returns:
        fit     (???)               No idea to be honest. I wrote this function almost six months ago.
        fit_eqn (string)            A clean representation of the polynomial fit. Intended to be inserted
                                    into a matplotlib plot as part of the legend or some such. 
                                    Uses 'LaTeX'.
        coeffs  (list, float)       A list of the coefficients of the polynomial fit, in decending powers.
    '''
    x = np.array(x)
    y = np.array(y)
    coeffs = np.polyfit(x, y, dg)
    fit = 0
    fit_eqn = "$\\rmfit:\ {} =".format(y_name)
    cf_str = ""
    for i in range(0, len(coeffs)):
        fit += coeffs[i] * (x ** (len(coeffs) - 1 - i))
        if i == 0:
            cf_str = "({:.3E})".format(coeffs[i])
        elif coeffs[i] < 0:
            cf_str = "-({:.3E})".format(-1*coeffs[i])
        else:
            cf_str = "+({:.3E})".format(coeffs[i])
        if (len(coeffs) - 1 - i) > 1:
            fit_eqn += " {} \\times {}^{}".format(cf_str, x_name, "{" + str((len(coeffs) - 1 - i)) + "}")
        elif (len(coeffs) - 1 - i) == 1:
            fit_eqn += " {} \\times {}".format(cf_str, x_name)
        else:
            fit_eqn += " {}".format(cf_str)

    fit_eqn += "$"
    return fit, fit_eqn, coeffs

def read_logf(log_n):
    '''
    plothelp.read_logf(log_n)
    
    Reads a .csv log file and outputs the columns as numpy arrays (float64).
    
    Parameters:
        log_n       (string)    Path of the log file to read.
    
    Returns:
        t           (np.array, float)     Number of seconds elapsed since the epoch.
        st          (np.array, float)     Number of seconds elapsed since logging begun.
        dr          (np.array, float)     Dynamo voltage readings.
        fdr         (np.array, float)     Filtered dynamo signal.
        cra         (np.array, float)     5A HECS voltage readings.
        crb         (np.array, float)     5A HECS voltage readings.
        pv          (np.array, float)     Value sent to potentiometer.
        T           (np.array, float)     Temperature in degrees centigrade.
        Vpz         (np.array, float)     Piezo sensor voltage reading.
        gamma_dot   (np.array, float)     Strain rate data (calculated from results).
        tau         (np.array, float)     Shear stress data (calculated from results).
        tag         (string)              Log tag, misc extra info about the experimental run.
    '''
    datf = pd.read_csv(log_n)
    
    t         =   np.array(datf['t'], np.float64)
    dr        =   np.array(datf['dr'], np.float64)
    fdr       =   np.array(datf['fdr'], np.float64)
    cra       =   np.array(datf['cra'], np.float64)
    crb       =   np.array(datf['crb'], np.float64)
    pv        =   np.array(datf['pv'], np.float64)
    T         =   np.array(datf['T'], np.float64)
    
    try:
        Vpz       =   np.array(datf['Vpz'], np.float64)
    except:
        Vpz       =   np.array(datf['Vpz1'], np.float64)
    
    try:
        tau       =   np.array(datf['tau'], np.float64)
        gamma_dot =   np.array(datf['gamma_dot'], np.float64)
    except:
        tau       = [0] * len(t)
        gamma_dot = [0] * len(t)
    
    st = t - t[0]
    
    # logs are normally saved in the following format:
    #rheometry_test_TAG_DATE_TIME.csv
    tag = log_n.split("_")[2]
    
    return t, st, dr, fdr, cra, crb, pv, T, Vpz, gamma_dot, tau, tag

def plot_logf(log_n):
    '''
    plothelp.plot_logf(log_n)
    
    Plots the data from the specified log. Four plots are produced on one figure:
        1. Shear stress v strain rate                               [TL]
        2. Piezo sensor voltage v time                              [TR]
        3. Piezo sensor voltage (normalised) v viscosity            [BR]
        4. Dynamo voltage v time and Filtered dynamo voltage v time [BL]
    The resulting figure is saved to the './plots' directory, keeping name similar 
    to its log file.
    
    Parameters:
        log_n   (string)    Path to log file to be plotted.
    '''
    
    __, st, dr, fdr, __, __, __, __, Vpz, gamma_dot, tau, __ = read_logf(log_n)
    
    #fdr = filter(st, dr) # placeholder until analogue filter is in place and somewhat working
    fpz = filter(st, Vpz)
    viscosity = list()
    Vpznormd = list()
    
    for i in range(0, len(st)):
        viscosity.append(tau[i] / gamma_dot[i])
        Vpznormd.append(fpz[i] / fdr[i])
    
    # Create figure
    f = plt.figure(figsize=(16,16))
    
    ### Plot 1: shear stress and strain rate ###
    ax = f.add_subplot(221) #top left
    ax.plot(gamma_dot, tau)
    ax.set_xlabel("$\\rmStrain\\ rate\\ [\\dot\\gamma],\\ (s^{-1})$")
    ax.set_ylabel("$\\rmShear\\ stress\\ [\\tau],\\ (Pa)$")
    
    ### Plot 2: piezo v time ###
    ax = f.add_subplot(222) #top right
    ax.plot(st, Vpz)
    ax.set_xlabel("$\\rmElapsed\\ time\\ [t],\\ (s)$")
    ax.set_ylabel("$\\rmPiezo\\ voltage\\ [V_{pz}],\\ (V)$")
    
    ### Plot 3: piezo (normalised) v viscosity ###
    ax = f.add_subplot(224) #bottom right
    ax.plot(viscosity, Vpznormd)
    ax.set_xlabel("$\\rmViscosity\\ [\\mu],\\ (Pa.s)$")
    ax.set_ylabel("$\\rmPiezo\\ voltage\\ (normalised)\\ [V_{pz,norm}],\\ (-)$")
    
    ### Plot 4: dynamo reading v time and filtered dr v time ###
    ax = f.add_subplot(223) #bottom left
    ax.plot(st, dr, color=(0, 0, 1, 0.25))
    ax.plot(st, fdr, color=(0, 0, 1, 1))
    ax.set_xlabel("$\\rmStrain\\ rate\\ [\\dot\\gamma],\\ (s^{-1})$")
    ax.set_ylabel("$\\rmShear\\ stress\\ [\\tau],\\ (Pa)$")
    
    plt.savefig("{}png".format(log_n[:-3]))
    

def get_significant_minimums(y, sens=10):
    '''
    plothelp.get_significant_minimums(y, **kwargs)
    
    Gets the most significantly minimum values of a dataseries.
    
    Parameters:
        y       (list, float)       List of y-values.
    
    **kwargs:
        sens    (integer)           Sensitivity; what percentage of (average y value) 
                                    constitutes significantly lower.
                                    
    Returns:
        res     (list, integer)     List of indexes of the points at which the Y value 
                                    is more than [sens]% lower than the average magnitude 
                                    of the y-values.
    '''
    
    av = np.average(y)
    
    diff = (sens / 100.0) * math.fabs(av)
    
    res = list()
    
    is_descending = False
    
    for i in range(1, len(y)):
        if y[i] < y[i - 1]:
            is_descending = True
        elif y[i] >= y[i - 1] and is_descending:
            is_descending = False
            if y[i] < (av - diff):
                res.append(i)
            
    return res
    
if __name__ == "__main__":
    #print __doc__
    import glob
    logs = glob.glob("./../logs/rhe*.csv")
    plot_logf(logs[0])
    
