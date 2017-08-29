'''
    Simple PI control in python.

    Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# System
from time import time
from time import sleep
import sys
import warnings

# 3rd Party
from matplotlib import use as mpluse
mpluse('Agg')
import matplotlib.pyplot as plt
import scipy.signal as sg
import numpy as np

class tf_pi_controller(object):
    '''
    Usage: 

    object = tf_pi_controller(tuning, set_point)

    Creates an instance of a PI controller.

    Parameters:
        tuning              (float, float)      Represents the gain parameters Kc and Kc/Ti respectively
        set_point           (float)             Represents the desired output from the process. Default is 0
        sample_time         (float)             Time between iterations in seconds. Default is 0.1

    Accessible Data:
        tuning              (float, float)      Represents the gain parameters Kc and Kc/Ti respectively
        set_point           (float)             Represents the desired output from the process. Default is 0

        Ys                  (list, float)       List of past process outputs.
        Us                  (list, float)       List of past controller outputs.
        Es                  (list, float)       List of past error values.

        remd_len            (integer)           'Remembered Length'; number of items to remember. Default is 100
                                                Higher number means better precision, but slower operation. RPi2 
                                                might not be able to take it.
    '''
    tuning = [0.0, 0.0]

    set_point = 0.0
    
    Ys = [0.0] * 2
    Us = [0.0] * 2
    Es = [0.0] * 2

    remd_len = 100
    
    def __init__(self, tuning, set_point=0.0, sample_time=0.1):
        '''
        object = tf_pi_controller(tuning, set_point)

        Creates an instance of a PI controller.
        
        Parameters:
            tuning              (float, float)  Represents the gain parameters Kc and Kc/Ti respectively
            set_point           (float)         Represents the desired output from the process. Default is 0
            sample_time         (float)         Time between iterations in seconds. Default is 0.1
        '''
        self.tuning = tuning  # Set tuning
        self.set_point = set_point  # Set set point
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # create controller transfer function
            # self.Gc = sg.TransferFunction((self.tuning[0], self.tuning[1]), (1, 0), dt=sample_time)
            # ^^ UNCOMMENT AND FIX PLS ^^
    
    def get_control_action(self, Y):
        '''
        tf_pi_controller.get_control_action(Y)
        
        With the current tuning, and the history of process outputs, 
        calculates the next control action to keep the process output 
        at the setpoint.
        
        Parameters:
            Y                   (float)         Value of the controlled process output.
        '''
        # set next input and error values in memory
        self.Ys.append(Y)
        self.Es.append(self.set_point - Y)
        
        # Tidy up memory
        if len(self.Ys) > 100: Ys = self.Ys[1:]
        if len(self.Es) > 100: Ys = self.Es[1:]

        # apply controller transfer function
        self.Us = self.Gc.output(self.Es, range(0, len(Es)))[1]  # 1st arr is T, 2nd is U, third is?
        
        return self.Us[-1]

    def do_sim(self, time_constant, steady_state_gain, sp=0, step_to=200, at_t=10, length=100):
        '''
        do_sim(time_constant, steady_state_gain, sp_step=200, at_t=10, length=100)
        
        Simulates the controller's response to a step change in set point.
        
        Parameters:
            time_constant       (float)         Coefficient of s in denominator of transfer function
            steady_state_gain   (float)         Numerator of transfer function.

        kwargs**:
            sp                  (float)         Initial set point. Default is 0.0
            step_to             (float)         Final set point. Defailt is 200.0
            at_t                (integer)       Number of samples to wait before stepping up. Default is 10
            length              (integer)       Number of samples overall to compute. Default is 100
        '''
        set_point = sp
        # Set up transfer functions
        Gp = sg.TransferFunction((steady_state_gain), (time_constant, 1))
        Gc = sg.TransferFunction((self.tuning[0], self.tuning[1]), (1, 0))
        
        # Create initial conditions
        Ys = [0, 0]
        Es = [0, 0]
        Us = [0, 0]

        for i in range(0, at_t):
            # Apply process transfer function to inputs
            Ys.append(Gp.output(Us, range(0, len(Us)))[1][-1])

            # Get new error
            Es.append(set_point - Ys[-1])

            # Apply controller transfer function to inputs
            Us = Gc.output(Es, range(0, len(Es)))[1]
    
        set_point = step_to

        for i in range(0, length - at_t):
            # Apply process transfer function to inputs
            Ys.append(Gp.output(Us, range(0, len(Us)))[1][-1])

            # Get new error
            Es.append(set_point - Ys[-1])

            # Apply controller transfer function to inputs
            Us = Gc.output(Es, range(0, len(Es)))[1]

        Ts = np.array(range(0, len(Ys))) * 0.1 - 0.2
        return (Ys, Es, Us, Ts)

if __name__ == "__main__":
    print __doc__
    print tf_pi_controller.__doc__
