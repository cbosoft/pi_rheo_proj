#
# filter.py
#
# A library containing different filtering/smoothing methods
#

# imports
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import wiener, filtfilt, butter, gaussian, freqz
from scipy.ndimage import filters
import scipy.optimize as op
import matplotlib.pyplot as plt

def gaussian(x, y):
	b = gaussian(39, 10)
	ga = filters.convolve1d(y, b/b.sum())
	return ga

def butterworth(nyf, x, y):
	b, a = butter(4, 1.5/nyf)
	fl = filtfilt(b, a, y)
	return fl
 
def wiener(y, sample_size=29, noise_magnitude=0.5):
	wi = wiener(y, mysize=sample_size, noise=noise_magnitude)
	return wi
 
def spline(x, y, samples=240):
	sp = UnivariateSpline(x, y, s=samples)
	return sp(x)
    
def filter(x, y, method="wiener"):
    output = [0] * 0
    if method == "wiener":
        output = wiener(y)
    elif method == "gaussian":
        output = gaussian(x, y)
    elif method == "butter":
        output = butterworth(0.5, x, y)
    elif method == "spline":
        output = spline(x, y)
    else:
        output = y
    return output
    
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
    c = filter(t, s)
    
    # Set up figure
    f = plt.figure(figsize=(8,8))
    ax = f.add_subplot(111)

    # Plot data and trendline
    ax.plot(t, s, 'b', color=(0,0,1,0.2))
    ax.plot(t, c, 'b')

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    #plt.title("$Moving\ Average\ Samples:\ {0}$".format(mav_l))

    # Show plot
    print "saving plot"
    #plt.show()
    plt.savefig("./figjamtest.png")
    plt.close(f)

    
