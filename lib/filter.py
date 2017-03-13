#
# filter.py
#
# A library containing different filtering/smoothing methods
#
# Smoothing: using all information surrounding a data point to obtain its true value
#
# Filtering: using information from before and including the current data point to obtain its true value
#
# Predicting: using information preceding the current data point to obtian its true value

# imports
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import wiener, filtfilt, butter, gaussian, freqz
from scipy.ndimage import filters
import scipy.optimize as op
import matplotlib.pyplot as plt

def ssqe(sm, s, npts):
	return np.sqrt(np.sum(np.power(s-sm,2)))/npts

def testGauss(x, y, s, npts):
	b = gaussian(39, 10)
	#ga = filtfilt(b/b.sum(), [1.0], y)
	ga = filters.convolve1d(y, b/b.sum())
	plt.plot(x, ga)
	print "gaerr", ssqe(ga, s, npts)
	return ga

def testButterworth(nyf, x, y, s, npts):
	b, a = butter(4, 1.5/nyf)
	fl = filtfilt(b, a, y)
	plt.plot(x,fl)
	print "flerr", ssqe(fl, s, npts)
	return fl
 
def testWiener(x, y, s, npts):
	wi = wiener(y, mysize=29, noise=0.5)
	plt.plot(x,wi)
	print "wieerr", ssqe(wi, s, npts)
	return wi
 
def testSpline(x, y, s, npts):
	sp = UnivariateSpline(x, y, s=240)
	plt.plot(x,sp(x))
	print "splerr", ssqe(sp(x), s, npts)
	return sp(x)

if __name__ == "__main__":
    # test script for testing
    
    # load up some noisy data
    logf = open("./test scripts/logs/smallx4.csv", "r")
    dat = logf.readlines()
    logf.close()
    
    # sort the loaded data into lists
    t = [0] * 0  # x, time
    s = [0] * 0  # y, speed
    
    for i in range(1, len(dat)):
        splt = dat[i].split(",", 5)
        t.append(float(splt[0]))
        s.append(float(splt[2]))
    
    # Apply filter
    g = testGauss(t, s, 0.9, len(t))
    #b = testButterworth(45, t, s, 1, len(t))
    w = testWiener(t, s, 1, len(t))
    b = testSpline(t, s, 1, len(t))
    
    # Set up figure
    f = plt.figure(figsize=(8,8))
    ax = f.add_subplot(111)

    # Plot data and trendline
    ax.plot(t, s, 'b', color=(0,0,1,0.2))
    #ax.plot(t, g, 'r')
    #ax.plot(t, b, 'g')
    ax.plot(t, w, 'b')

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    #plt.title("$Moving\ Average\ Samples:\ {0}$".format(mav_l))

    # Show plot
    print "saving plot"
    plt.savefig("./figjamtest.png")
    plt.close(f)

    
