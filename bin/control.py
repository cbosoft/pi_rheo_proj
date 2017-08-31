'''
    Simple PI control in python.

    Author: Caner Durmusoglu (bilgi@ivmech.com)
    Adapted by: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# System
from time import time
from time import sleep

class pid_controller(object):
    '''
    Usage: 

    object = pid_controller(tuning, set_point)

    Creates an instance of a PI controller.

    Parameters:
        tuning              (float, float)      Represents the gain parameters Kc and Kc/Ti respectively
        set_point           (float)             Represents the desired output from the process. Default is 0
    '''
    
    def __init__(self, tuning, set_point=0.0):
        '''
        object = pid_controller(tuning, set_point)

        Creates an instance of a PI controller.
        
        Parameters:
            tuning              (float, float)  Represents the gain parameters Kc and Kc/Ti respectively
            set_point           (float)         Represents the desired output from the process. Default is 0
            sample_time         (float)         Time between iterations in seconds. Default is 0.1
        '''
        self.tuning = tuning 
        self.set_point = set_point
        
        self.int_err = 0.0
        self.windeup_guard = 20.0
        
        self.lov = 0.0
        
        self.clear()
    
    def clear(self):
        '''
        pid_controller.clear()
        
        Resets stored variables to default/zero.
        '''
        
        self.set_point      = 0.0
        self.pterm          = 0.0
        self.iterm          = 0.0
        self.dterm          = 0.0
        self.lerr           = 0.0
        self.int_err        = 0.0
        self.windup_guard   = 20.0
        self.lov            = 0.0
    
    def get_control_action(self, value):
        '''
        pid_controller.get_control_action(value)
        
        Calculates the next control action to keep the process output 
        at the setpoint.
        
        Parameters:
            value               (float)         Value of the controlled process output.
        
        Returns:
            lov                 (float)         Value of control action/output: "last output value"
        '''
        error = self.set_point - value
        
        self.current_time = time()
        dt = self.current_time - self.last_time
        derr = err - lerr
        
        self.pterm = self.tuning[0] * err
        self.iterm += err * dt
        
        if (self.iterm < -self.windup_guard):
            self.iterm = -self.windup_guard
        elif (self.iterm > self.windup_guard):
            self.iterm = self.windup_guard
        
        self.dterm = 0.0
        if dt > 0: self.dterm = derr / dt
        
        self.last_time = self.current_time
        self.lerr = err
        
        self.lov = self.pterm + (self.tuning[1] * self.iterm) + (self.tuning[2] * self.dterm)
        
        return lov

if __name__ == "__main__":
    print __doc__
    print tf_pi_controller.__doc__
