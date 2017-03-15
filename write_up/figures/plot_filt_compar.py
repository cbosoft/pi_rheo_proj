# not sure if working?

import sys

sys.path.append('./../../lib')

from filter import filter
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import wiener, filtfilt, butter, gaussian, freqz
from scipy.ndimage import filters
import scipy.optimize as op
import matplotlib.pyplot as plt

def filterff(path_file, filter_method="butter", A=0.314, B=0.314):
    # load up some noisy data
    print "loading data"
    logf = open(path_file, "r")
    dat = logf.readlines()
    logf.close()
    
    # sort the loaded data into lists
    t = [0] * 0  # x, time
    s = [0] * 0  # y, speed
    start = 0.0  # start time (since epoch)
    st = [0] * 0 # specific time (time since run begun, seconds)
    
    print "sorting..."

    splt = dat[1].split(",", 5)
    t.append(float(splt[0]))
    s.append(float(splt[2]))
    start = t[0]
    st.append(0.0)

    for i in range(2, len(dat)):
        splt = dat[i].split(",", 5)
        t.append(float(splt[0]))
        s.append(float(splt[2]))
        st.append(t[i - 1] - start)
    
    print "sorted"
    print "applying filter"
    # Apply filter
    c = filter(t, s, method=filter_method)
    return st, s, c

if __name__ == "__main__":
    # test script for testing
    # wiener averages too much and loses data
    # don't use spline - graphical method has little correlation to actual data
    # (tuned) butterworth seems to work well (A=2, nyf=0.05  

    method = "gauss"

    # load up some noisy data
    flt = [0.0] * 1
    # intermittent load
    x, y, flt[0] = filterff("./../../logs/intermittent_load_short.csv", filter_method=method, A=10, B=0.01)
    
    for i in range(0, 10):
        flt.append(filter(x, y, method="butter", A=(2 + i), B=(0.01 * (i + 1))))
    
    # simple 
    
    print "plotting"
    # Set up figure
    f = plt.figure(figsize=(15,15))
    ax = f.add_subplot(111)
    plt.title("$Filter\ \"Tuning\"\ Comparison$", fontsize=24)

    # Plot data and trendline
    ax.plot(x, y, 'b', color=(0,0,1,0.2))
    for i in range(2, 3):
        for j in range(8, 9):
            print "A={0}, B={1}, plotting...".format((i), (0.01 * j))
            ax.plot(x, filter(x, y, method="butter", A=(i), B=(0.01 * j)))

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    #plt.title("$Filter\ Type:\ {0}$".format(method), fontsize=20)

    # Show plot
    print "saving plot"
    #plt.show()
    plt.savefig("./fig_filter_{0}_compare.png".format(method))
    plt.close(f)
