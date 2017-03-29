import sys

sys.path.append('./../../bin')

from filter import filter
import numpy as np
import scipy.optimize as op
import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib as mpl


def filterff(path_file, filter_method="butter", a=1, b=1):
    # load up some noisy data
    logf = open(path_file, "r")
    dat = logf.readlines()
    logf.close()
    
    # sort the loaded data into lists
    t = [0] * 0  # x, time
    s = [0] * 0  # y, speed
    start = 0.0  # start time (since epoch)
    st = [0] * 0 # specific time (time since run begun, seconds)
  

    splt = dat[1].split(",", 5)
    t.append(float(splt[0]))
    s.append(float(splt[2]))
    st.append(0.0)

    for i in range(2, len(dat)):
        splt = dat[i].split(",", 5)
        t.append(float(splt[0]))
        s.append(float(splt[2]))
        st.append(t[i - 1] - t[0])
    
    # Apply filter
    c = filter(t, s, method=filter_method, A=a)
    return st, s, c

if __name__ == "__main__":
    # test script for testing
    # wiener averages too much and loses data
    # don't use spline - graphical method has little correlation to actual data
    # (tuned) butterworth seems to work well (A=4, nyf=0.08)

    method = "gauss"

    # load up some noisy data, apply first filter
    # load up some noisy data
    #logf = open("./../../logs/intermittent_load_short.csv", "r")
    logf = open("./../../logs/long_cal_old.csv", "r")
    dat = logf.readlines()
    logf.close()
    
    # sort the loaded data into lists
    t = [0] * 0  # time
    y = [0] * 0  # y, speed
    x = [0] * 0 # x, specific time (time since run begun, seconds)
  

    splt = dat[1].split(",", 5)
    t.append(float(splt[0]))
    y.append(float(splt[2]))
    x.append(0.0)

    for i in range(2, len(dat) / 10):
        splt = dat[i].split(",", 5)
        t.append(float(splt[0]))
        y.append(float(splt[2]))
        x.append(t[i - 1] - t[0])

    # Apply filters
    f_spline = filter(x, y, method="spline")
    f_wiener = filter(x, y, method="wiener")
    f_gaussian = filter(x, y, method="gaussian")
    f_butter = filter(x, y, method="butter")

    # Set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)

    # Shorten the data
    x = x[10000:20000]
    y = y[10000:20000]

    # Plot data and trendline

    # Original data
    ax.plot(x, y, color=(0,0,1,0.2))
    
    # Filtered data
    ax.plot(x, f_spline[10000:20000], 'b')

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    # Save plot
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_filt_compar_spline.png")
    plt.close(f)

    ##################################
    # Set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)

    # Plot data and trendline

    # Original data
    ax.plot(x, y, color=(0,0,1,0.2))
    
    # Filtered data
    ax.plot(x, f_wiener[10000:20000], 'b')

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    # Save plot
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_filt_compar_wiener.png")
    plt.close(f)

    ##################################
    # Set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)

    # Plot data and trendline

    # Original data
    ax.plot(x, y, color=(0,0,1,0.2))
    
    # Filtered data
    ax.plot(x, f_gaussian[10000:20000], 'b')

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    # Save plot
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_filt_compar_gaussian.png")
    plt.close(f)

    ##################################
    # Set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)

    # Plot data and trendline

    # Original data
    ax.plot(x, y, color=(0,0,1,0.2))
    
    # Filtered data
    ax.plot(x, f_butter[10000:20000], 'b')

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    # Save plot
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_filt_compar_butter.png")
    plt.close(f)
