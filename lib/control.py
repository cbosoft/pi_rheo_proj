#
# control.py
#
# Controller class. Provides support for controling a process using python.
# Simply gets a control action based upon a set point and an input value.
#
# Uses the valocity discrete time algorithm for control action.
#
# To be implemented in the future:
#	# Continuous time algorithm
#	# Auto tuning

# Imports
from time import time


class PIDcontroller(object):
    KP = 0  # Proportional Gain
    KI = 0  # Integral Gain
    KD = 0  # Derivative Gain
    P_On = False
    I_On = False
    D_On = False

    set_point = 0  # Set point used to find the error

    ca = [0, 0, 0]  # three most recent values of the control action
    e = [0, 0, 0]  # three most recent values of the error

    time_of_last = 0  # time of last run, in seconds
    sample_time = 0.1  # time between runs, in seconds

    # class initialisation method
    def __init__(self, KP_=0, KI_=0, KD_=0, sample_time_=0.1, set_point=0):

        self.sample_time = sample_time_  # initial sample time

        if (KP_ == 0):  # if KP is zero, turn off proportional control
            self.P_On = False
        else:
            self.P_On = True
            self.KP = KP_

        if (KI_ == 0):  # if KI is zero, turn off integral control
            self.I_On = False
        else:
            self.I_On = True
        self.KI = KI_

        if (KD_ == 0):
            self.D_On = False  # if KD is zero, turn off derivative control
        else:
            self.D_On = True
            self.KD = KD_

    # simple method that moves values up in array
    def shift_arrs(self):
        temp = self.ca[1]
        self.ca[1] = self.ca[2]
        self.ca[0] = temp
        temp = self.e[1]
        self.e[1] = self.e[2]
        self.e[0] = temp

    # get required control action
    def get_control_action(self, u_val):
        # Control action is a function of the k parameters, the previous control actions, the previous errors, and the sample time

        # Get actual time between samples
        if (self.time_of_last == 0):
            self.time_of_last = time()
            self.sample_time = 0.1  # rough initial sample time
        else:
            self.sample_time = time() - self.time_of_last  # set sample time to actual time between samples
            self.time_of_last = time()

        self.shift_arrs()  # move stored values down, making space for next set

        self.e[2] = self.set_point - u_val  # get new error

        self.ca[2] = self.ca[1]  # use velocity discrete time algorithm to obtain the required control action

        if (self.P_On):
            self.ca[2] += self.KP * (self.e[2] - self.e[1])

        if (self.I_On):
            self.ca[2] += self.KI * self.sample_time * self.e[2]

        if (self.D_On):
            self.ca[2] += (self.KD / self.sample_time) * (self.e[2] - (2 * self.e[1]) + self.e[0])
        return self.ca[2]
    
    def tune(self, time_constant, steady_state_gain, steps=20, maxs=5):
        #for each possible tuning arrangement...
        #gets response to a unit step at t=0
        
        #get list of total number of maximums
        
        #check responses for quickest rise with non-zero number of maximums (but less than 5)
        
        current_tuning = (self.KP, self.KI, self.KP)
        
        points = [[[0, 0], [0, 0]]] * 2 # x, y
        maxima_count = [0] * 2
        first_xs = [0] * 2
        for sP in range(0, maxs):
            self.KP = 0 + sP * (maxs / steps)
            for sI in range(0, maxs):
                self.KI = 0 + sP * (maxs / steps)
                for sD in range(0, maxs):
                    self.KD = 0 + sP * (maxs / steps)
                    this_points = self.do_sim(time_constant, steady_state_gain)
                    points.append(this_points)
                    (a, b) = self.count_maxima(this_points)
                    maxima_count.append(a)
                    first_xs.append(b)
                        
    def do_sim(self, time_constant, steady_state_gain):
        self.set_point = 1
        resp = [[0.0, 0.0], [0.0, 0.0]]
        y = [0.0, 0.0]
        ca = [0.0, 0.0]
        for i in range(0, 100):
            y[0] = y[1]
            ca[0] = ca[1]
            y[1] = ((time_constant - self.sample_time) / time_constant) * y[0] + ((steady_state_gain * self.sample_time) / time_constant) * ca[0]
            ca[1] = self.get_control_action(y[1])
            resp.append([i, y[1]])
            print y[1]
        return resp
    
    def count_maxima(self, points):
        gradient = 0
        last_gradient = 0
        max_cnt = 0
        first_max_x = 0.0
        last_y = points[0][1]
        maxima_count = 0
        
        for i in range(0,len(points)):
            if points[i][1] > last_y:
                gradient = 1
            elif points[i][1] == last_y:
                gradient = 0
            else:
                gradient = -1
                
            if ((gradient < 0) and (last_gradient >= 0)):
                maxima_count += 1
                if (maxima_count == 1):
                    first_max_x = points[i][0]
                    
            last_gradient = gradient
            last_y = points[i][1]
        return [maxima_count, first_max_x]
        
        
if __name__ == "__main__":
    a = PIDcontroller()
    a.tune(2, 1)
    #TEST AND REDO
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        