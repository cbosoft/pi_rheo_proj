'''
    Wrappers for selected filtering functions from scipy
    
    Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# System
from enum import Enum as enum

# 3rd Party
import numpy as np  # for maths
from scipy.interpolate import UnivariateSpline  # for splining
from scipy.signal import wiener, filtfilt, butter, gaussian  # for fliter-making
from scipy.ndimage import filters # for applying filters

class ftype(enum):
    gaussian    = 0
    butterworth = 1
    wiener      = 2
    spline      = 3
        
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
    
def filter(x, y, method=ftype.butterworth, A=0.314, B=0.314):
    '''
    Filter for filtering noise out from a signal.
    
    Arguments:
        x           The x data for the singal (usually time)
        y           The noisy signal data
        method      Which filter to use. 'ftype.butterworth' by default.
        A, B        Parameters of the filter to be used.
    
    Returns:
        List of filtered y-values.
    '''

    use_A = True
    use_B = True

    if A == 0.314:
        use_A = False

    if B == 0.314:
        use_B = False

    output = [0] * 0

    if method == ftype.wiener:
        
        if not use_A:
            A = 29
        
        output = wienerf(y, sample_size=A)

    elif method == ftype.gaussian:

        if not use_A:
            A = 51

        if not use_B:
            B = 7
        
        output = gaussianf(x, y, sample_size=A, sigma=B)

    elif method == ftype.butterworth:

        if not use_A:
            A = 2

        if not use_B:
            B = 0.008

        output = butterworthf(x, y, order=A, nyq=B)

    elif method == ftype.spline:
        
        if not use_A:
            A = 100

        output = splinef(x, y, sample_size=A)

    else:

        output = y
    
    return output
    
    
print __doc__
print filter.__doc__
    
