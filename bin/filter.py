#
# filter.py
#
# A library containing different filtering/smoothing methods
#

# imports
import numpy as np  # for maths
from scipy.interpolate import UnivariateSpline  # for splining
from scipy.signal import wiener, filtfilt, butter, gaussian  # for fliter-making
from scipy.ndimage import filters # for applying filters
        
def gaussianf(x, y, sample_size=51, sigma=7):
	b = gaussian(sample_size, sigma)
	ga = filters.convolve1d(y, b/b.sum())
	return ga

def butterworthf(x, y, order=4, nyq=0.008):
	b, a = butter(order, nyq)
	fl = filtfilt(b, a, y)
	return fl
 
def wienerf(y, sample_size=29):
	wi = wiener(y, sample_size)
	return wi
 
def splinef(x, y, sample_size=100):
	sp = UnivariateSpline(x, y, s=sample_size)
	return sp(x)
    
def filter(x, y, method="butter", A=0.314, B=0.314):
    """
    Filter for filtering noise out from a signal.
    
    Arguments:
    x - The x data for the singal (usually time)
    y - The noisy signal data
    method - Which filter to use. "butter" by default.
    A, B - Parameters of the filter to be used. Pre-set by default to most optimal.
           See individual filter functions for specific definitions.
    
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
        
        if not use_A:
            A = 29
        
        output = wienerf(y, sample_size=A)

    elif method == "gaussian":

        if not use_A:
            A = 51

        if not use_B:
            B = 7
        
        output = gaussianf(x, y, sample_size=A, sigma=B)

    elif method == "butter":

        if not use_A:
            A = 2

        if not use_B:
            B = 0.008

        output = butterworthf(x, y, order=A, nyq=B)

    elif method == "spline":
        
        if not use_A:
            A = 100

        output = splinef(x, y, sample_size=A)

    else:

        output = y
    
    return output
    
    

    
