#
# control.py
#
# Controller class. Provides support for controling a process using python.
# Simply gets a control action based upon a set point and an input value.
#
# Uses the valocity discrete time algorithm for control action.
#
# (TODO: Continuous time implementation?)
#

# Imports
from time import time
from time import sleep
import sys
import matplotlib.pyplot as plt


class PIDcontroller(object):
    KP = 0.0  # Proportional Gain
    KI = 0.0  # Integral Gain
    KD = 0.0  # Derivative Gain

    set_point = 0.0  # Set point used to find the error

    ca = [0.0, 0.0, 0.0]  # three most recent values of the control action
    e = [0.0, 0.0, 0.0]  # three most recent values of the error

    time_of_last = 0  # time of last run, in seconds
    sample_time = 0.1  # time between runs, in seconds
    manual_sample = False

    loud = False
    
    def __init__(self, KP=0, KI=0, KD=0, sample_time="AUTO", set_point=0):
        '''
        object = control.PIDcontroller(**kwargs)
        
        Initialise PID controller class.
        
        Controller uses discrete-time PID controller.
        
        Must be tuned before use, this can be done manually (manually setting the values of KP, Ki, and KD), or automatically (using the PIDcontroller.tune function) if you have a 1st order model of the process.
        
        kwargs:
        KP - Controller proportional gain. Default is 0.
        KI - Controller integral gain. Default is 0.
        KD - Controller derivative gain. Default is 0.
        sample_time - Length of time interval between samples. Default is "AUTO" - sample_time is automatically calculated.
        set_point - the "goal" for the control system. Default is 0
        '''
        
        self.ifl("CONTROLLER INITIALISING")
        if str(sample_time) == "AUTO":
            self.ifl("    auto_sample ON")
            self.manual_sample = False
        else:
            self.ifl("    auto_sample OFF")
            self.sample_time = sample_time
            self.manual_sample = True

        self.ifl("    set_point {0:.1f}".format(set_point))
        self.set_point = set_point
        
        self.ifl("    KP {0:.1f}".format(KP))
        self.KP = KP        
        self.ifl("    KI {0:.1f}".format(KI))
        self.KI = KI        
        self.ifl("    KD {0:.1f}".format(KD))
        self.KD = KD

    def shift_arrs(self):
        '''
        shift_arrs()
        
        Shifts the stored error and control actions down. Required by the PID algorithm implementation.
        '''
        
        self.ca = self.ca[1:]
        self.e = self.e[1:]
        self.ca.append(0.0)
        self.e.append(0.0)
        
    def ifl(self, mesg):
        '''
        ilf(mesg)
        
        if loudness is turned on (if self.load is True), mesg is printed to stdout.
        
        mesg - (string) message to (maybe) print
        '''
        
        if self.loud: print mesg
    
    def get_control_action(self, u_val):
        '''
        get_control_action(u_val)
        
        Gets the appropriate control action, based upon tuning,
        the previous control actions and errors, and the sample_time.
        
        u_val - (float) the controller input
        
        returns: (float) the recommended change to the current control action (delta control action)
        '''

        # Get actual time between samples
        if (self.manual_sample == False):
            if (self.time_of_last == 0):
                self.time_of_last = time()
                self.sample_time = 0.1 
            else:
                self.sample_time = time() - self.time_of_last
                self.time_of_last = time()

        self.shift_arrs()  # move stored values down, making space for next set

        self.e[-1] = (float(self.set_point) - float(u_val))  # get new error
        
        delta_e = self.e[-1] - self.e[0]

        self.ca[-1] = 0.0

        self.ca[-1] += float(self.KP) * delta_e

        self.ca[-1] += (float(self.KI) * float(self.sample_time)
        * float(self.e[-1]))

        self.ca[-1] += ((float(self.KD) / float(self.sample_time)) * delta_e)
        # (float(self.e[2]) - (2 * float(self.e[1])) + float(self.e[0])))
        return self.ca[-1]

    def tune(self, time_constant, steady_state_gain, steps=20, pmx=(0.0, 1.0),imx=(0.0, 1.0), dmx=(0.0, 1.0), ise_tuning=True):
        '''
        tune(time_constant, steady_state_gain, **kwargs)
        
        Tunes the controller parameters based upon a specified first order model.
        
        The model is a first order transfer function of the form:
        
            Y(s) / U (s) = SSG / (TC * s + 1)
        
        Required arguments:
        time_constant - model time constant
        steady_state_gain - model steady_state_gain
        
        kwargs:
        steps - the number of iterations to make over each parameter. Total number of iterations is steps^3. Default is 20.
        pmx - (tuple float), "Proportional Min maX", the range of proportional gain values iterated over. Default is (0.0, 1.0).
        imx - (tuple float), range of integral gain values to iterate over. Default is (0.0, 1.0).
        dmx - (tuple float), range of derivative gain values to iterate over. Default is (0.0, 1.0).
        '''
        
        # for each possible tuning arrangement...
        # gets response to a unit step at t=0

        # get list of total number of maximums

        # check responses for quickest rise with non-zero number of maximums
        # (but less than 5)

        # current_tuning = (self.KP, self.KI, self.KP)
        print "Initialising"
        points = [[[0, 0], [0, 0]]] * 0  # x, y
        maxima_count = [0] * 0
        ise = [0] * 0
        first_xs = [0] * 0

        # initial tuning
        self.KP = 0.0
        self.KI = 0.0
        self.KD = 0.0

        # tuning history
        tuning_hist = [(0, 0, 0)] * 0

        print "Checking paramter combinations..."
        # start running through all the possible tuning arrangements
        for sP in range(0, steps):
            self.KP = float(pmx[0]) + float(sP * (float(pmx[1]) / float(steps)))
            for sI in range(0, steps):
                self.KI = float(imx[0]) + float(sI * (float(imx[1]) / float(steps)))
                for sD in range(0, steps):
                    # self.KD = float(dmx[0]) + float(sD * (float(dmx[1]) / float(steps)))
                    #print ("getting tuned response: " + str(self.KP) + ", " +
                    #str(self.KI) + ", " + str(self.KD))
                    # print str(sP) + ", " + str(sI) + ", " + str(sD)
                    (this_points, insqer) = self.do_sim(time_constant, steady_state_gain)
                    points.append(this_points)
                    (a, b) = self.count_maxima(this_points)
                    maxima_count.append(a)
                    ise.append(insqer)
                    first_xs.append(b)
                    tuning_hist.append([self.KP, self.KI, self.KD])
                    prog = int(((sP * steps) + sI) * 100 / (steps ** 2))
                    sys.stdout.write(('\r[ {0} ] {1}% [ KP={2:.3f}, KI={3:.3f}]').format(str('#' * (prog / 2)) + str(' ' * (50 - (prog / 2))), prog, self.KP, self.KI))
                    sys.stdout.flush()

        self.ifl("\nOptimising...")
        for i in range(0, len(points)):
            if (maxima_count[i] > 0 and maxima_count[i] < 5):
                pass
            else:
                first_xs[i] = 10000

        smallest_x = 1000.0
        at_indx = 0
        for i in range(0, len(points)):
            if (first_xs[i] < smallest_x):
                at_indx = i
                smallest_x = first_xs[i]
        
        
        smallest_ise = 1000000
        ise_at = 0
        for i in range(0, len(ise)):
            if ise[i] < smallest_ise:
                smallest_ise = ise[i]
                ise_at = i

        (a, b, c) = tuning_hist[at_indx]
        self.ifl("GEO TUNE RESULTS: KP={0}, KI={1}, KD={2}".format(a, b, c))

        (a, b, c) = tuning_hist[ise_at]
        self.ifl("ISE TUNE RESULTS: KP={0}, KI={1}, KD={2}".format(a, b, c))
        
        if (ise_tuning):
            self.KP, self.KI, self.KD = tuning_hist[ise_at]
        else:
            self.KP, self.KI, self.KD = tuning_hist[at_indx]

        if (ise_tuning):
            return (tuning_hist[at_indx], ise[at_indx])
        else:
            return (tuning_hist[ise_at], ise[ise_at])
        #return (points[at_indx], tuning_hist, at_indx)

    def do_sim(self, time_constant, steady_state_gain, length=100, manual_sample_time=0.1, horiz_return=True):
        '''
        do_sim(time_constant, steady_state_gain, **kwargs)
        
        Uses the tuned parameters to simulate the controllers responses to a step change in set point.
        
        The model is a first order transfer function of the form:
        
            Y(s) / U (s) = SSG / (TC * s + 1)
        
        Required arguments:
        time_constant - model time constant
        steady_state_gain - model steady_state_gain
        
        kwargs:
        length - the number of samples to calculate response for. Default is 100.
        manual_sample_time - if the controller is using manual sample times, the value set here will be used for the sample time. Default is 0.1.
        '''
        
        # save controller settings and change it for the simulation
        ts = self.set_point
        m_on = self.manual_sample
        self.manual_sample = True
        st = self.sample_time
        self.sample_time = manual_sample_time
        self.set_point = 100
        resp = [0.0, 0.0] * 0
        x_s = [0] * 0
        y_s = [0] * 0
        y = [0.0, 0.0]
        pv = 64

        # reset memory
        self.reset_memory()
        ise = 0.0
    
        # simulate!
        for i in range(0, length):
            y[0] = y[1]

            #y[1] = (((float(time_constant) - float(self.sample_time)) / float(time_constant)) * float(y[0])
            #+ ((float(steady_state_gain) * float(self.sample_time)) / float(time_constant)) * float(self.ca[-1]))
            
            #y[1] = float(self.ca[-1]) * float(steady_state_gain) / ((float(time_constant) / float(self.sample_time)) + 1)

            pv += self.ca[-1]

            y[1] = 5.130 * pv + 15.275
            
            self.get_control_action(y[-1])
            resp.append([i, y[-1]])
            x_s.append(i)
            y_s.append(y[-1])
            try:
                ise += (self.e[-2] ** 2)
            except OverflowError:
                ise += 10000
            # print y[1]

        # return settings to the way they were
        self.set_point = ts
        self.sample_time=st
        self.manual_sample = m_on
        if not horiz_return:
            return (x_s, y_s)
        else:
            return (resp, ise)

    def reset_memory(self):
        '''
        reset_memory()
        
        Causes the script to forget the previous control actions and errors - starts a fresh.
        '''
        
        self.ca = [0.0, 0.0, 0.0]
        self.e = [0.0, 0.0, 0.0]


    def count_maxima(self, points):
        '''
        count_maxima(points)
        
        Counts the number of maxima in a response curve.
        
        Required arguments:
        points - (list float) a list of the responses.
        
        returns:
        [maxima_count, first_max_x]
        maxima_count - number of maxima in the response.
        first_max_x - list index of the location of the first maxima.
        '''
        gradient = 0
        last_gradient = 0
        first_max_x = 0.0
        last_y = points[0][1]
        maxima_count = 0

        for i in range(0, len(points)):
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
            # print "maxima: " + str(maxima_count)
        return [maxima_count, first_max_x]


if __name__ == "__main__":
    f = plt.figure(figsize=(8,8))
    ax = f.add_subplot(111)

    a = PIDcontroller(KP=0.10, KI=0.20, KD=0, set_point=200.0, sample_time=0.01)
    ise = "n/a"
    print "AUTO TUNE OFF, USING PRE-TUNING::"
    print "    Kp: " + str(a.KP)
    print "    Ki: " + str(a.KI)
    print "    Kd: " + str(a.KD)
    print "    ISE: " + str(ise)

    if (False):
        # # # # FIRST SIM RESPONSE # # # # 
        ys = [0] * 0
        pvs = [0] * 0
        cur_ca = 0.0
        cur_pv = 78
        t_len = 10
        xs = [0] * 0
        xs.append(0)
        ys.append((4.292 * float(cur_pv)) + 144.927)
        for i in range(1, int(t_len / a.sample_time) + 1):
            cur_ca = a.get_control_action((4.292 * float(cur_pv)) + 144.927)
            cur_pv += cur_ca
            
            if cur_pv < 0:
                cur_pv = 0
            elif cur_pv > 128:
                cur_pv = 128

            ys.append((4.292 * float(cur_pv)) + 144.927)
            pvs.append(cur_pv)
            # sleep(0.1)
            prog = int((i) * 100 / (t_len / a.sample_time))
            sys.stdout.write(('\r[ {0} ] {1}%').format(str('#' * (prog / 2)) + str(' ' * (50 - (prog / 2))), prog))
            sys.stdout.flush()
            xs.append(i * a.sample_time)

        # check against simulated response
        #r, ise = a.do_sim(0.072, 4.687, length=t_len)
        
        #s_xs = [0] * 0
        #s_ys = [0] * 0

        #for i in range(0, len(r)):
        #    s_xs.append(r[i][0])
        #    s_ys.append(r[i][1])

        # # # # PLOT # # # # 
        ax.plot(xs, ys, label="KP={0}, KI={1}, KD={2}".format(a.KP, a.KI, a.KD))
        #ax.plot(s_xs, s_ys, 'g')

        ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
        ax.set_ylabel("$Response,\ RPM$\n", ha='center', va='center', fontsize=24)

        # # # # SAVE PLOT # # # # 
        print "\nsaving plot"
        plt.legend()
        plt.savefig("./figresp.png")
        plt.close(f)
    
    if (True):
        cur = 400.0
        print "TESTING:"
        print "    set_point = {0}\n    current_speed = {1}\n    control_action = {2}".format(a.set_point, cur, a.get_control_action(cur))