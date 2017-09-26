'''
auto_tune.py

implementation of the Ziegler-Nichols controller tuning method in python.

Author: Christopher Boyle (christopher.boyle.101@strath.ac.uk)
'''

from sys import path
from time import sleep
from scipy.optimize import leastsq

path.append("./../bin/")

import control as c
from motor import motor as m

mot = m(poll_logging=False)
mot.startpoll(controlled=False)
mot.set_dc(50)

print "warming up motor"

sleep(3)

Ku = 0.0
Tu = 0.0

mot.start_control()


## sets Kp to 0
## increases until Kp=Ku: when response is oscillating
## period of this oscillation is Tu
## Ku and Tu are used to obtain the parameters for the 
## ideal tuning, or at least, a starting point

def residual(vars, x, y, eps_data):
    amp = params['amp']
    pshift = params['phase']
    freq = params['frequency']
    decay = params['decay']

    model = amp * sin(x * freq  + pshift) * exp(-x*x*decay)

    return (y-model)/eps_data

def is_osc(x, y):
    '''
    is_osc(x, y)

    takes data and determines whether it is stably oscillating

    Fits a sin wave to the data. If the fit works, then the data is oscillating.
    '''

    vars = [10.0, 0.2, 3.0, 0.007]
    eps_data = 1.0
    out = leastsq(residual, vars, args=(x, y, eps_data))

    amp = out[0][0]
    phase = out[0][1]
    freq = out[0][2]
    decay = out[0][3]

    model = amp * np.sin(x * freq  + phase) * np.exp(-x*x*decay)

    if (np.log10(abs(decay)) > -5): 
        return False
    else:
        return True

    