#
# filter.py
#
# A library containing different filtering/smoothing methods
#

# imports
import numpy as np  # for maths
from scipy.interpolate import UnivariateSpline  # for splining
from scipy.signal import wiener, filtfilt, butter, gaussian  # for 
from scipy.ndimage import filters
import scipy.optimize as op
import matplotlib.pyplot as plt

def gaussianf(x, y, A=39, B=10):
	b = gaussian(A, B) # a here is samples and B is a number or something
	ga = filters.convolve1d(y, b/b.sum())
	return ga

def butterworthf(x, y, A=4, B=0.08):
	b, a = butter(A, B)
	fl = filtfilt(b, a, y)
	return fl
 
def wienerf(y, sample_size=29, noise_magnitude=0.5):
	wi = wiener(y, sample_size, noise_magnitude) #, mysize=sample_size, noise=noise_magnitude)
	return wi
 
def splinef(x, y, samples=240):
	sp = UnivariateSpline(x, y, s=samples)
	return sp(x)
    
def filter(x, y, method="butter", A=0.314, B=0.314):
    """
    Filter for filtering noise out from a signal.
    
    Arguments:
    x - The x data for the singal (usually time)
    y - The noisy signal data
    method - Which filter to use. "butter" by default.
    A, B - Parameters of the filter to be used. Pre-set by default to most optimal. Not recommended to be changed.
    
    Returns:
    A list of filtered y-values, the same length as the input data.
    """

    use_A = True
    use_B = True

    if A == 0.314:
        use_A = False

    if B == 0.314:
        use_B = False

    output = [0] * 0

    if method == "wiener":

        output = wienerf(y)

    elif method == "gaussian":

        if not use_A:
            A = 39

        if not use_B:
            B = 10
        
        output = gaussianf(x, y, A, B)

    elif method == "butter":

        if not use_A:
            A = 2

        if not use_B:
            B = 0.05

        output = butterworthf(x, y, A, B)

    elif method == "spline":

        output = splinef(x, y)

    else:

        output = y
    
    return output
    
    

    
