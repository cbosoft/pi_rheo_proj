#! usr/bin/env python

'''
    Controller object for the concentric cylinder rotational rheometer from a Raspberry Pi 2.

    Allows the running of tests and control of the hardware, and the logging of data, for the
    prototype jamming study rheometer.

    Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

debug = False

print "Loading packages.."

## Included in python...
print "\tPython packages..."
import time
import sys
import math
from math import sin
from math import cos
import copy
import random
from glob import glob
import platform
from enum import Enum as enum

## Third party
print "\t3rd Party Packages..."
import numpy as np
import pandas as pd
import curses
import matplotlib
from sympy.parsing.sympy_parser import parse_expr as pe
import sympy as sp

try:
    import spidev
except:
    debug = True
    
## RPi-Rheo packages
print "\tRPi-Rheo Packages"
import resx
from filter import filter as filt_r
from plothelp import fit_line
from plothelp import plot_fit
from plothelp import read_logf
from motor import motor

def linux_distribution():
  try:
    return platform.linux_distribution()
  except:
    return "N/A"

try:
    dist = platform.linux_distribution()
except:
    debug = True

version = resx.version

class inputs(enum):
    none_   = 1
    enum_   = 2
    string_ = 3

class rheometer(object):
    '''
    object = rheometer(**kwargs)
    
    Creates a new instance of a rheometer controller class object. Uses motor.py to control the rotation
    of a cylinder in a concentric cylinder rotational rheometer. Data is logged from various sensors and
    used to calculate the rheology of a test solution, with an aim to better understand jamming.
    
    **kwargs:
        motor_params        (dict)      Dictionary of keyword arguments to use when setting up the motor.
                                        One entry by default:
                                            'log_dir' : './../logs'
    '''
    
    def __init__(self, motor_params={'log_dir':'./../logs'}):
        '''
        object = rheometer(**kwargs)
        
        Creates a new instance of a rheometer controller class object. Uses motor.py to control the rotation
        of a cylinder in a concentric cylinder rotational rheometer. Data is logged from various sensors and
        used to calculate the rheology of a test solution, with an aim to better understand jamming.
        
        **kwargs:
            motor_params        (dict)      Dictionary of keyword arguments to use when setting up the motor.
                                            One entry by default:
                                                'log_dir' : './../logs'
        '''
        self.mot = motor(**motor_params)
    
    #################################################################################################################### DISPLAY
    def display(self, blurb, options, selected=0, input_type=inputs.enum_):
        global stdscr
        global debug
        stdscr.clear()
        stdscr.border(0)

        # RPi-R header
        mode_string = "MOTOR OFF"
        if self.mot.ldc: mode_string = "!! MOTOR ON !!"
        if debug: mode_string = "!! DEBUG !!"
            
        stdscr.addstr(3, 1,  r"                                 _        _                                     ")
        stdscr.addstr(4, 1,  r"                      _ __ _ __ (_)  _ __| |__   ___  ___                       ")
        stdscr.addstr(5, 1,  r"                     | '__| '_ \| | | '__| '_ \ / _ \/ _ \                      ")
        stdscr.addstr(6, 1,  r"                     | |  | |_) | |_| |  | | | |  __/ (_) |                     ")
        stdscr.addstr(7, 1,  r"                     |_|  | .__/|_(_)_|  |_| |_|\___|\___/                      ")
        stdscr.addstr(8, 1,  r"                          |_|  Raspberry Pi Rheometer v{}                    ".format(version))
        stdscr.addstr(9, 1,  r"                                                                                ")
        stdscr.addstr(10, 1,  r"{}".format(mode_string.center(80)))

        blurbheight = 12

        # Display Blurb
        for i in range(0, len(blurb)):
            stdscr.addstr(blurbheight + i, 1, blurb[i].center(80))
        
        # Show Options
        for i in range(0, len(options)):
            if (selected == i and input_type == inputs.enum_):
                stdscr.addstr(blurbheight + len(blurb) + i + 1, 1, options[i].center(80), curses.A_STANDOUT)
            else:
                stdscr.addstr(blurbheight + len(blurb) + i + 1, 1, options[i].center(80))

        # Get Input
        stdscr.addstr(0,0, "")
        stdscr.refresh()
        if input_type == inputs.enum_:
            res = stdscr.getch()
        elif input_type == inputs.string_:
            curses.echo()
            stdscr.addstr(blurbheight + len(blurb) + len(options) + 2, 10, "".center(60, "."))
            res = stdscr.getstr(blurbheight + len(blurb) + len(options) + 2, 10, 60)
        else:
            res = 10

        # Return
        if input_type == inputs.string_:
            curses.noecho()
        elif res == curses.KEY_UP:
            # up arrow, reduce selection
            if selected == 0:
                selected = len(options) - 1
            else:
                selected -= 1
                
            res = self.display(blurb, options, selected, input_type)
        elif res == curses.KEY_DOWN:
            # down arrow, increase selection
            if selected == len(options) - 1:
                selected = 0
            else:
                selected += 1

            res = self.display(blurb, options, selected, input_type)
        elif res == curses.KEY_ENTER or res == 10 or res == 13:
            res = selected
        else:
            res = self.display(blurb, options, selected, input_type)
        return res
        

    #################################################################################################################### SIMPLE MODE
    def simple_mode(self, initsel=0):
        global stdscr
        global debug
        
        blurb =     [
                    " " #"Welcome to RPi-R: Simple rheometry recording with a Raspberry Pi",
                    ]
        options =   [
                    "Run test",                     # 0
                    "Calibrate Motor",              # 1
                    "Quit"                          # 4
                    ]
        res = self.display(blurb, options, selected=initsel)
        
        if res == 0: ################################################################################################### RUN TEST: 0
            # Run sample
            
            # Get settings
            
            # Run length
            inp_k = False
            extra_info = " "
            
            while not inp_k:
                blurb = ["Run sample - setup",
                         "",
                         "{}{}".format("Length:".center(40), "--".center(40)),
                         "{}{}".format("Function:".center(40), "--".center(40)),
                         "{}{}".format("Log tag:".center(40), "--".center(40)),
                         "",
                         extra_info,
                         "Enter run length (seconds)"]
                options = [""]
                
                length = self.display(blurb, options, input_type=inputs.string_)
                
                inp_k = True
                
                try:
                    length = int(length)
                except:
                    inp_k = False
                    extra_info = "Input not recognised (must be an integer)"
                    
            # strain rate function
            inp_k = False
            extra_info = " "
            
            while not inp_k:
                blurb = ["Run sample - setup",
                         "",
                         "{}{}".format("Length:".center(40), str(length).center(40)),
                         "{}{}".format("Function:".center(40), "--".center(40)),
                         "{}{}".format("Log tag:".center(40), "--".center(40)),
                         "",
                         extra_info,
                         "Enter strain rate function (inverse seconds)",
                         "",
                         "Input in form of an expression (gamma dot = ...)",
                         "",
                         "Max GD = 250, min GD = 5.",
                         "",
                         "A special case: GD = linear from <MIN> to <MAX>"]
                options = [""]
                
                gd_expr = self.display(blurb, options, input_type=inputs.string_)
                
                gd_expr_split = gd_expr.split()
                
                ### Special Cases ###
                if gd_expr_split[0] == "linear":
                    gd_min = gd_expr_split[2]
                    gd_max = gd_expr_split[4]
                    gd_expr = "{0} + (({1} - {0}) / {2}) * t".format(gd_min, gd_max, length)
                    
                inp_k = True
                
                try:
                    t = 2
                    gd = sp.Symbol('gd')
                    expr = pe(gd_expr) - gd
                    val = sp.solve(expr, gd)
                    if len(val) > 1: raise Exception("you dun entered it rong lol")
                    a = eval(str(sp.solve(expr, gd)[0]))
                except:
                    inp_k = False
                    extra_info = "Input not recognised (ensure it is a function of 't', or a constant)"
            
            # Run tag
            inp_k = False
            extra_info = " "
            
            while not inp_k:
                blurb = ["Run sample - setup",
                         "",
                         "{}{}".format("Length:".center(40), str(length).center(40)),
                         "{}{}".format("Function:".center(40),"gd = {} (s^-1)".format(gd_expr).center(40)),
                         "{}{}".format("Log tag:".center(40), "--".center(40)),
                         "",
                         extra_info,
                         "Enter identifier for the run: (test material composition etc)"]
                options = [""]
                
                tag = self.display(blurb, options, input_type=inputs.string_)
                
                gd_expr_split = gd_expr.split()
                
                ### Special Cases ###
                if gd_expr_split[0] == "linear":
                    gd_min = gd_expr_split[2]
                    gd_max = gd_expr_split[4]
                    gd_expr = "{0} + (({1} - {0}) / {2}) * t".format(gd_min, gd_max, length)
                    
                inp_k = True
                
                try:
                    tag = str(tag)
                except:
                    inp_k = False
                    extra_info = "Input not recognised (how on earth did you input a non-string?!)"
            
            blurb = ["Run sample - setup",
                     "",
                     "{}{}".format("Length:".center(40), str(length).center(40)),
                     "{}{}".format("Function:".center(40),"gd = {} (s^-1)".format(gd_expr).center(40)),
                     "{}{}".format("Log tag:".center(40), tag.center(40)),
                     ""]
            options = ["Continue", "Quit"]
            res = self.display(blurb, options)
            
            if res == 1: return 1
            
            ln = self.run_test(tag, length, gd_expr)
            
            blurb = ["Run sample - complete", "", "output log saved as {}".format(ln)]
            options = ["Continue"]
            res = self.display(blurb, options)
        elif res == 1: ################################################################################################# RECAL: 1
            # Recalibrate                
            ### Part 2: Motor Calibration ###
            blurb = [   "Motor Calibration",
                        "",
                        "The torque output of the motor will be related to the current it draws.",
                        "Required are at least two newtonian reference fluids of known viscosity.",
                        "",
                        "This calibration does not need to be done every time the rheometer is used,",
                        "but should be done once in a while."
                    ]
            options = [ "Continue", "Cancel" ]
               
            res = self.display(blurb, options)
                
            if res == 1: x = 1 + "t"  # cancelations are exceptional
              
            ref_logs  = list()
            ref_viscs = list()
                
            finished = False
            count = 1
                
            while not finished:
                inp_k = False
                while not inp_k:
                    blurb = [   "Motor Calibration: fluid {}".format(count),
                                "",
                                "Fill the cylinder with a reference fluid up to the \"15ml min\" line.",
                                "Then raise the platform so that the liquid level raises to the \"15ml max\" line.",
                                "",
                                "Enter the viscosity of the fluid: (Pa.s)"                                
                            ]
                    options = [" "]
                        
                    str_nom_visc = self.display(blurb, options, input_type=inputs.string_)
                    try:
                        ref_viscs.append(float(str_nom_visc))
                        inp_k = True
                    except:
                        inp_k = False
                    
                blurb = [   "Motor Calibration: fluid {}".format(count),
                            "",
                            "Now the fluid will be run for 10 minutes at a strain rate of ~125 (s^-1).",
                        ]
                options = [ "Continue", "Cancel" ]
                    
                res = self.display(blurb, options)
                    
                if res == 1: x = 1 + "t"
                
                ref_log = self.run_test("newt_ref_1", 600, 125, title="Reference {} Test".format(count), ln_prefix="motor_calibration")
                ref_logs.append(ref_log)
                    
                count += 1
                    
                if count == 2:
                    finished = False
                else: # count > 2
                    blurb = [   "Motor Calibration",
                                "",
                                "Do you wish to use further reference fluids? ({} so far)".format(count - 1) ]
                    options = ["Yes", "No"]
                    res = self.display(blurb, options)
                        
                    if res == 1: finished = True
                            
            blurb = [ "Motor Calibration",
                      "",
                      "Calculating..." ]

            self.display(blurb, list(), input_type=inputs.none_)
                
            I_EMFs = list()
            T_MSs  = list()
                
            for i in range(0, len(ref_logs)):
                blurb = [ "Motor Calibration",
                      "",
                      "Calculating...",
                      "    {}".format(ref_logs[i]) ]

                self.display(blurb, list(), input_type=inputs.none_)
                __, st, __, __, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, T, Vpz, Vms, gamma_dot, tau, tag = read_logf(ref_logs[i])
                I_MS = resx.get_current(cra, crb)
                I_CO = resx.get_current_coil(Vms)
                I_EMF = [0.0] * len(I_MS)
                self.display(["{}  {}  {}".format(len(I_MS), len(I_CO), len(I_EMF))], [], input_type=inputs.none_)
                for j in range(0, len(I_MS)):
                    I_EMF[j] = I_MS[j] - I_CO[j]
                I_EMFs.append(np.average(I_EMF))
                    
                stress = ref_viscs[i] * np.average(gamma_dot)
                torque = resx.get_torque(stress, 15)
                T_MSs.append(np.average(torque))
                
            __, f_eqn, mot_cal = plot_fit(I_EMFs, T_MSs, 1, x_name="Iemf", y_name="Tau")
            
            blurb = ["Motor Calibration",
                     "",
                     "Complete!",
                     "",
                     "Previous fit:",
                     "\tTau = Iemf * {} + {}".format(resx.cal_TauIemf[0], resx.cal_TauIemf[1]),
                     "",
                     "New fit:",
                     "\tTau = Iemf * {} + {}".format(mot_cal[0], mot_cal[1])]
            options = ["Save results", "Discard"]
                
            res = self.display(blurb, options)
                
            if res == 0:
                resx.cal_TauIemf = mot_cal
                resx.writeout()
        else:
            return 4
        return 1
            
    #################################################################################################################### run_test()
    def run_test(self, tag, length, gd_expr, title="Rheometry Test", ln_prefix="rheometry_test"):
        # Calculate initial GD for warm up
        gd_expr = str(gd_expr)
        gd = sp.Symbol('gd')
        t = 0.0
        expr = pe(gd_expr) - gd
        gd_val = eval(str(sp.solve(expr, gd)[0]))
        self.mot.setup_gpio()
        self.mot.set_dc(50)

        #self.display([title, "", ""], [""], input_type=inputs.none_)
        ln = "./../logs/{}_{}_{}.csv".format(ln_prefix, tag, time.strftime("%d%m%y_%H%M", time.gmtime()))
        blurb = [
                title,
                "(warming up motor)",
                "{}{}".format("Supply voltage:".center(40), "-- V".center(40)),
                "{}{}".format("Target strain rate:".center(40), "-- (s^-1)".center(40)),
                "{}{}".format("Current rotation rate:".center(40), "-- (RPM)".center(40)),
                "{}{}".format("Current strain rate:".center(40), "-- (s^-1)".center(40)),
                "{}{}".format("Time remaining:".center(40), "--s".center(40)),
                "",
                "[{}]".format(" " * 40)
                ]
        options = [" "]
        self.display(blurb, options, input_type=inputs.none_)
        time.sleep(1)
        self.set_strain_rate(50)
        time.sleep(3)

        if not debug: self.mot.start_poll(name=ln, controlled=False)
        
        for i in range(0, length):
            t = float(copy.copy(i))
            
            expr = pe(gd_expr) - gd
            
            gd_val = eval(str(sp.solve(expr, gd)[0]))
            
            self.set_strain_rate(gd_val)
            
            width = 40
            perc = int(math.ceil((i / float(length)) * width))
            neg_perc = int(math.floor(((float(length) - i) / length) * width))
            fspd = np.average(self.mot.f_speeds)
            rspd = np.average(self.mot.r_speeds)
            aspd = (fspd + rspd) * 0.5
            blurb = [
                    title,
                    "",
                    "{}{}".format("Supply voltage:".center(40), "{:.3f} V".format((self.mot.volts[7] * 4.0)).center(40)),
                    "{}{}".format("Target strain rate:".center(40), "{:.3f} (s^-1)".format(gd_val).center(40)),
                    "{}{}".format("Current rotation rate:".center(40), "{:.3f} (RPM)".format(aspd).center(40)),
                    "{}{}".format("Current strain rate:".center(40), "{:.3f} (s^-1)".format(resx.get_strain(aspd)).center(40)),
                    "{}{}".format("Time remaining:".center(40), "{}s".format(length - i).center(40)),
                    "",
                    "[{}{}]".format("#" * perc, " " * neg_perc)
                    ]
            options = [" "]
            self.display(blurb, options, input_type=inputs.none_)
            time.sleep(1)
        
        self.mot.clean_exit()
        
        blurb = [
                title,
                "",
                "Processing results..." ]
        
        options = [" "]
        self.display(blurb, options, input_type=inputs.none_)
        
        if debug:
            time.sleep(1)
        else:
            self.calculate_viscosity(ln)
        
        blurb = [
                title,
                "",
                "Processing complete!" ]
        
        options = [" "]
        self.display(blurb, options, input_type=inputs.none_)
        
        return ln
       
    #################################################################################################################### set_strain_rate()   
    def set_strain_rate(self, value):
        if self.mot.control_stopped:
            #desired_speed = value * (resx.ocir - resx.icor) / resx.icor  # in rads
            #desired_speed = desired_speed * 60 / (2 * np.pi)  # in rpms
            #set_pv = int((desired_speed - resx.cal_Vnl[1]) / resx.cal_Vnl[0])
            #set_vo = (set_pv * 0.066) + 2.422
            #set_dc = set_vo / (3.33 * 4)
            self.mot.set_dc(15)
        else:
            self.mot.update_setpoint(value)

    #################################################################################################################### calculate_viscosity()
    def calculate_viscosity(self, ln):
        '''
        rheometer.calculate_viscosity(ln)
        
        Opens up a log file and calculates viscosity from the data within, saving results.
        
        Parameters:
            ln          path to logfile to edit
        
        Overview
        --------
        The calculation is performed using two methods. The first stems from an energy balance, but
        seems to not give great results. The second comes from simple analysis of the inner workings
        of the motor, and gives somewhat accurate results. Additional columns added to log: gamma_dot
        (strain rate, in inverse seconds), tau (shear stress, in pascal-seconds), mu_en_bal (viscosity 
        calculated using the energy balance method), and mu_current_relation (viscosity calculated using
        the second method).
        
        Strain Rate
        -----------
        Directly related to the rotational speed of the cylinder, assuming no wall-slip
    
            gamma_dot = omega * (inner_radius / (outer_radius - inner_radius))
        
        Shear Stress, Method 1: Energy Balance
        ------------------------
        Simply taking an energy balance over the motor yields an equation giving the torque
        output as a function of the input power (current x voltage), the efficiency, and the
        rotational speed.
        
            power = omega * tau = efficiency * current * voltage 
           .: tau = (efficiency * current * voltage) / omega
        
        Shear Stress, Method 2: Current relation
        --------------------------
        Torque (tau) is a function of current only. Some current is used purely by the
        resistance in the coil. Most of the current is used creating the EMF which drives
        The motor. Let these currents be termed Ico for the current used uselessly in the
        coils and Iemf for the useful EMF producing current. Ims is the total current 
        supplied to the motor.
        
            Ims = Ico + Iemf  --> Iemf = Ims - Ico
            tau = Kti * Iemf
        
         .: tau = Kti * (Ims - Ico)
         
         Viscosity
         ---------
         Knowing the shear stress and the strain rate, the viscosity can be calculated using newtons law of 
         viscosity:
         
            mu = tau / gamma_dot
        
        Once calculated, this is then added to the log file.
        '''
        t, st, f_spd0, r_spd0, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, T, Vpz, Vms, __, __, tag = read_logf(ln)
        
        # Energy balance method calculation
        omega   = list()
        for i in range(0, len(f_spd1)):
             omega.append((f_spd1[i] + r_spd1[i] + f_spd2[i] + r_spd2[i]) / 4.0)
        omega   = np.array(omega, np.float64)

        current = resx.get_current(cra, crb)
        voltage = Vms
        
        omega   = filt_r(st, omega)
        current = filt_r(st, current)
        
        ################################################################################
        # Strain rate. #################################################################
        
        gamma_dot = resx.get_strain(omega)
        
        ################################################################################
        # Energy balance. ##############################################################
        
        efficiency = 0.8
        tau       = (efficiency * current * voltage) / omega  
        mu_energy_balance_method = tau / gamma_dot
        
        ################################################################################
        # Current relation. ############################################################
        
        current_coil = resx.get_current_coil(voltage)
        tau = resx.cal_TauIemf[0] * (current - current_coil) + resx.cal_TauIemf[1]
        mu_current_relation = tau / gamma_dot
        
        ################################################################################
        # Updating log. ################################################################
        
        logf = open(ln, "w")
        logf.write("t,f_spd0,r_spd0,f_spd1,r_spd1,f_spd2,r_spd2,cra,crb,T,Vpz,Vms,gamma_dot,tau,mu_en_bal,mu_current_relation\n")
        for i in range(0, len(t)):
            line = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                    t[i], f_spd0[i], r_spd0[i], f_spd1[i], r_spd1[i], #5
                    f_spd2[i], r_spd2[i], cra[i], crb[i], #4
                    T[i], Vpz[i], voltage[i], gamma_dot[i], tau[i], #5
                    mu_energy_balance_method[i], mu_current_relation[i]) #2
            logf.write(line)
        logf.close()
        
if __name__ == "__main__":
    #x = raw_input()
    # setup curses window
    bigscr = curses.initscr()
    stdscr = curses.newwin(35, 82, 1, 1)
    #stdscr.border(0)
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    
    # if debug: no logging
    if debug:
        mparams={'poll_logging':False}
    else:
        mparams={'poll_logging':True}

    # start up rheometer
    r = rheometer(motor_params=mparams)
    
    menu_mode_simple = True
    catch_mode_on = True
    
    if "-r" in sys.argv: catch_mode_on = False # raw operation, errors are not caught.

    if not catch_mode_on:
        a = r.simple_mode()
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
    else:
        try:
            res = 0
            while res != 4:
                res = r.simple_mode(initsel=res)
        except:
            pass
        else:
            pass
        finally:
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()
