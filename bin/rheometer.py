#! usr/bin/env python

'''
    Control script for the concentric cylinder rotational rheometer from a Raspberry Pi 2.

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

def CAE(Exception):
    '''Terrible practice, but handy for easily cancelling out of a deep nest'''
    pass

######################################################################################################################## DISPLAY
def display(blurb, options, selected=0, input_type=inputs.enum_):
    global stdscr
    global debug
    global mot
    stdscr.clear()
    stdscr.border(0)

    # RPi-R header
    mode_string = "MOTOR OFF"
    if mot.ldc: mode_string = "!! MOTOR ON !!"
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
            
        res = display(blurb, options, selected, input_type)
    elif res == curses.KEY_DOWN:
        # down arrow, increase selection
        if selected == len(options) - 1:
            selected = 0
        else:
            selected += 1

        res = display(blurb, options, selected, input_type)
    elif res == curses.KEY_ENTER or res == 10 or res == 13:
        res = selected
    else:
        res = display(blurb, options, selected, input_type)
    return res
    

######################################################################################################################## MENU
def menu(initsel=0):
    global stdscr
    global debug
    global mot
    
    blurb =     [
                " " #"Welcome to RPi-R: Simple rheometry recording with a Raspberry Pi",
                ]
    options =   [
                "Run test",                     # 0
                "Calibrate Motor",              # 1
                "Quit"                          # 4
                ]
    res = display(blurb, options)
    
    if res == 0: ####################################################################################################### RUN TEST: 0
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
            
            length = display(blurb, options, input_type=inputs.string_)
            
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
            
            gd_expr = display(blurb, options, input_type=inputs.string_)
            
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
            
            tag = display(blurb, options, input_type=inputs.string_)
            
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
        res = display(blurb, options)
        
        if res == 1: return 1
        
        ln = run_test(tag, length, gd_expr)
        
        blurb = ["Run sample - complete", "", "output log saved as {}".format(ln)]
        options = ["Continue"]
        res = display(blurb, options)
    elif res == 1: ##################################################################################################### RECAL: 1
        # Recalibrate
        ### Part 1: Current Calibration ###
        len_ccal = 300
        blurb = [   "Current Calibration",
                    "",
                    "The current drawn due to inefficiencies in the motor will be found in this test.",
                    "",
                    "The cylinders must be empty, but in position as if a test was being run.",
                    "The test will take around {} minutes.".format(float(len_ccal) / 60.0),
                    ""
                ]
        options = [ "Start", "Skip to motor calibration" ]
        res = display(blurb, options)

        if not res:
            cur_log = "./../logs/ccal_{}.csv".format(time.strftime("%d.%m.%y-%H%M", time.gmtime()))
            if not debug: mot.start_poll(name=cur_log, controlled=False)
            for i in range(0, len_ccal):
                dc = (100.0 / (len_ccal - 1)) * i
                mot.set_dc(dc)
                width = 40
                perc = int(math.ceil((i / float(len_ccal)) * width))
                neg_perc = int(math.floor(((float(len_ccal) - i) / len_ccal) * width))
                fspd = np.average(mot.f_speeds)
                rspd = np.average(mot.r_speeds)
                aspd = (fspd + rspd) * 0.5
                aspd_rads = aspd * 2.0 * np.pi / 60.0
                vms = mot.volts[7] * 4.0
                if vms == 0: vms = 10**-10
                gd = resx.get_strain(aspd_rads)
                if gd == 0: gd = 10**-10
                ico = resx.get_current_coil(vms)
                ims = resx.get_current(mot.volts[2])
                iemf = ims - ico
                tau = resx.cal_TauIemf[0] * iemf + resx.cal_TauIemf[1]
                if tau < 0: tau = 0.0
                mu = tau / gd
                blurb = [
                        "Current Calibration",
                        "",
                        "{}    {}".format("Electronics".center(38), "Mechanics".center(38)),
                        "{}{}    {}{}".format("Vms:".center(19), "{:.3f} V".format(vms).center(19), "omega:".center(19), "{:.3f} rad/s".format(aspd).center(19)),
                        "{}{}    {}{}".format("Ims:".center(19), "{:.3f} A".format(ims).center(19), "gamma dot:".center(19), "{:.3f} (s^-1)".format(gd).center(19)),
                        "{}{}    {}{}".format("Iemf:".center(19), "{:.3f} A".format(iemf).center(19), "tau:".center(19), "{:.3f} Pa".format(tau).center(19)),
                        "{}{}    {}{}".format("PWM DC:".center(19), "{:.3f} %".format(dc).center(19), "mu:".center(19), "{:.2E} Pa.s".format(mu).center(19)),
                        "",
                        "{}s to go...".format(len_ccal - i).center(80),
                        "[{}{}]".format("#" * perc, " " * neg_perc)
                        ]
                options = [" "]
                display(blurb, options, input_type=inputs.none_)
                time.sleep(1)
            mot.clean_exit()
            __, st, __, __, __, __, __, __, cra, __, __, __, Vms, __, __, __ = read_logf(cur_log)
            Vms = filt_r(st, Vms)
            cra = filt_r(st, cra)
            Ims = resx.get_current(cra)
            blurb = [
                        "Current Calibration",
                        "",
                        "Processing data..."
                        ]
            options = [" "]
            display(blurb, options, input_type=inputs.none_)
            fit, fit_eqn, coeffs = plot_fit(Vms, Ims, 1, x_name="Vms", y_name="Ico", outp="./../plots/cal_cur.png")
            blurb = ["Current Calibration",
             "",
             "Complete! Plot saved as \"./../plots/cal_cur.png\"",
             "",
             "Previous fit:",
             "\tIco = Vms * {} + {}".format(resx.cal_IcoVms[0], resx.cal_IcoVms[1]),
             "",
             "New fit:",
             "\tIco = Vms * {} + {}".format(coeffs[0], coeffs[1])]
            options = ["Save results", "Discard"]
            
            res = display(blurb, options)
            
            if res == 0:
                resx.cal_IcoVms = coeffs
                resx.writeout()
            
        ### Part 2: Motor Calibration ###
        blurb = [   "Motor Calibration",
                    "",
                    "The torque output of the motor will be related to the current it draws.",
                    "Required are at least two newtonian reference fluids of known viscosity.",
                    "",
                    "This calibration does not need to be done every time the rheometer is used,",
                    "but should be done once in a while."
                ]
        options = [ "Continue", "Back to main menu" ]
           
        res = display(blurb, options)
            
        if res == 1: raise CAE ## Cancellations are exceptional
          
        ref_logs  = list()
        ref_viscs = list()
        ref_nams  = list()
        
        cal_len = 120
            
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
                    
                str_nom_visc = display(blurb, options, input_type=inputs.string_)
                try:
                    ref_viscs.append(float(str_nom_visc))
                    inp_k = True
                except:
                    inp_k = False
            inp_k = False

            while not inp_k:
                blurb = [   "Motor Calibration: fluid {}".format(count),
                            "",
                            "What fluid is it?"                                
                        ]
                options = [" "]
                    
                str_ref_nam = display(blurb, options, input_type=inputs.string_)
                blurb = [   "Motor Calibration: fluid {}".format(count),
                            "",
                            "\"{}\"?".format(str_ref_nam)
                        ]
                options = ["That is correct", "Oops! Typo"]
                    
                rep = display(blurb, options, input_type=inputs.enum_)
                if rep == 0:
                    inp_k = True
                    ref_nams.append(str_ref_nam)
                
            blurb = [   "Motor Calibration: fluid {}".format(count),
                        "",
                        "Now the fluid will be run for {} minutes at a strain rate of ~125 (s^-1).".format(float(cal_len) / 60.0),
                    ]
            options = [ "Continue", "Cancel" ]
                
            res = display(blurb, options)
                
            if res == 1: x = 1 + "t"
            ref_log = "./../logs/mcal_{}_{}_pas_{}.csv".format(ref_nams[-1], ref_viscs[-1], time.strftime("%d.%m.%y-%H%M", time.gmtime()))
            self.run_test("newt_ref", cal_len, 125, title="Reference {} Test".format(count), ln_override=ref_log)
            ref_logs.append(ref_log)
                
            count += 1
                
            if count == 2:
                finished = False
            else: # count > 2
                blurb = [   "Motor Calibration",
                            "",
                            "Do you wish to add further reference fluids? ({} so far)".format(count - 1) ]
                options = ["Yes", "No"]
                res = display(blurb, options)
                    
                if res == 1: finished = True
        
        self.mot_cal(ref_logs)
    else:
        return 4
    return 1

######################################################################################################################## mot_cal()
def mot_cal(self, ref_logs):
    global mot
    blurb = [ "Motor Calibration",
              "",
              "Calculating..." ]
    display(blurb, list(), input_type=inputs.none_)
            
    I_EMFs = list()
    T_MSs  = list()
            
    for i in range(0, len(ref_logs)):
        blurb = [ "Motor Calibration",
                  "",
                  "Calculating...",
                  "    {}".format(ref_logs[i]) ]

        display(blurb, list(), input_type=inputs.none_)
        __, st, __, __, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, T, Vpz, Vms, gamma_dot, tau, tag = read_logf(ref_logs[i])
        
        # mcal_[name]_[viscosity]_pas_[date+time].csv
        viscosity = float(ref_logs[i].split('_')[2])
        
        I_MS = resx.get_current(cra)
        I_CO = resx.get_current_coil(Vms)
        I_EMF = [0.0] * len(I_MS)
        display(["{}  {}  {}".format(len(I_MS), len(I_CO), len(I_EMF))], [], input_type=inputs.none_)
        for j in range(0, len(I_MS)):
            I_EMF[j] = I_MS[j] - I_CO[j]
        I_EMFs.append(np.average(I_EMF))
                
        stress = viscosity * np.average(gamma_dot) # pa = pa.s * (1/s)
        torque = resx.get_torque(stress, 15)
        T_MSs.append(torque)
            
    __, f_eqn, mot_cal = plot_fit(I_EMFs, T_MSs, 1, x_name="Iemf", y_name="Tau", outp="./../plots/cal_mot.png")
        
    blurb = ["Motor Calibration",
             "",
             "Complete! Plot saved as \"./../plots/cal_mot.png\"",
             "",
             "Previous fit:",
             "\tTau = Iemf * {} + {}".format(resx.cal_TauIemf[0], resx.cal_TauIemf[1]),
             "",
             "New fit:",
             "\tTau = Iemf * {} + {}".format(mot_cal[0], mot_cal[1])]
    options = ["Save results", "Discard"]
            
    res = display(blurb, options)
            
    if res == 0:
        resx.cal_TauIemf = mot_cal
        resx.writeout()
    
######################################################################################################################## run_test()
def run_test(tag, length, gd_expr, title="Rheometry Test", ln_prefix="rheometry_test", ln_override=None):
    global mot
    # Calculate initial GD for warm up
    gd_expr = str(gd_expr)
    gd = sp.Symbol('gd')
    t = 0.0
    expr = pe(gd_expr) - gd
    gd_val = eval(str(sp.solve(expr, gd)[0]))
    mot.setup_gpio()
    mot.set_dc(50)

    #display([title, "", ""], [""], input_type=inputs.none_)
    ln = "./../logs/{}_{}_{}.csv".format(ln_prefix, tag, time.strftime("%d%m%y_%H%M", time.gmtime()))
    if ln_override != None: ln = ln_override
    blurb = [
                        title,
                        "(warming up motor)",
                        "{}    {}".format("Electronics".center(38), "Mechanics".center(38)),
                        "{}{}    {}{}".format("Vms:".center(19), "-- V".center(19), "omega:".center(19), "-- rad/s".center(19)),
                        "{}{}    {}{}".format("Ims:".center(19), "-- A".center(19), "gamma dot:".center(19), "-- (s^-1)".center(19)),
                        "{}{}    {}{}".format("Iemf:".center(19), "-- A".center(19), "tau:".center(19), "-- Pa".center(19)),
                        "{}{}    {}{}".format("PWM DC:".center(19), "-- %".center(19), "mu:".center(19), "-- Pa.s".center(19)),
                        "",
                        "",
                        "[{}]".format(" " * 40)
            ]
    options = [" "]
    display(blurb, options, input_type=inputs.none_)
    time.sleep(1)
    set_strain_rate(gd_val)
    time.sleep(3)

    if not debug: mot.start_poll(name=ln, controlled=True)
    
    for i in range(0, length):
        gd_expr = str(gd_expr)
        gd = sp.Symbol('gd')
        t = float(copy.copy(i))
        expr = pe(gd_expr) - gd
        gd_val = eval(str(sp.solve(expr, gd)[0]))
        set_strain_rate(gd_val)
        
        width = 40
        perc = int(math.ceil((i / float(length)) * width))
        neg_perc = int(math.floor(((float(length) - i) / length) * width))
        fspd = np.average(mot.f_speeds)
        rspd = np.average(mot.r_speeds)
        aspd = (fspd + rspd) * 0.5
        aspd_rads = (aspd * 2 * np.pi) / 60.0
        dc   = mot.ldc
        vms  = mot.volts[7] * 4.0
        if vms == 0: vms = 10**-10
        gd = resx.get_strain(aspd_rads)
        if gd == 0: gd = 10**-10
        ico = resx.get_current_coil(vms)
        ims = resx.get_current(mot.volts[2])
        iemf = ims - ico
        T = resx.cal_TauIemf[0] * iemf + resx.cal_TauIemf[1]
        tau = resx.get_stress(T, 15)
        if tau < 0: tau = 0.01
        mu = tau / gd
        tau = T
        blurb = [
                title,
                "",
                "{}    {}".format("Electronics".center(38), "Mechanics".center(38)),
                "{}{}    {}{}".format("Vms:".center(19), "{:.3f} V".format(vms).center(19), "omega:".center(19), "{:.3f} rad/s".format(aspd).center(19)),
                "{}{}    {}{}".format("Ims:".center(19), "{:.3f} A".format(ims).center(19), "gamma dot:".center(19), "{:.3f} (s^-1)".format(gd).center(19)),
                "{}{}    {}{}".format("Iemf:".center(19), "{:.3f} A".format(iemf).center(19), "tau:".center(19), "{} Pa".format(tau).center(19)),
                "{}{}    {}{}".format("PWM DC:".center(19), "{:.3f} %".format(dc).center(19), "mu:".center(19), "{:.2E} Pa.s".format(mu).center(19)),
                "",
                "{}s to go...".format(length - i).center(80),
                "[{}{}]".format("#" * perc, " " * neg_perc)
                ]
        options = [" "]
        display(blurb, options, input_type=inputs.none_)
        time.sleep(1)
    
    mot.clean_exit()
    
    blurb = [
            title,
            "",
            "Processing results..." ]
    
    options = [" "]
    display(blurb, options, input_type=inputs.none_)
    
    if debug:
        time.sleep(1)
    else:
        calculate_viscosity(ln)
    
    blurb = [
            title,
            "",
            "Processing complete!" ]
    
    options = [" "]
    display(blurb, options, input_type=inputs.none_)
    
    return ln
   
######################################################################################################################## set_strain_rate()   
def set_strain_rate(value):
    global mot
    if mot.control_stopped:
        #desired_speed = value * (resx.ocir - resx.icor) / resx.icor  # in rads
        #desired_speed = desired_speed * 60 / (2 * np.pi)  # in rpms
        #set_pv = int((desired_speed - resx.cal_Vnl[1]) / resx.cal_Vnl[0])
        #set_vo = (set_pv * 0.066) + 2.422
        #set_dc = set_vo / (3.33 * 4)
        mot.set_dc(value / 20)
    else:
        mot.pidc.set_point = value

def solver_expr(expression, t=0.0, T=None):
    global mot
    if T == None: T = mot.temperature_c
    expr = str(expression)
    y = sp.Symbol('y')
    t = float(copy.copy(t))
    T = float(copy.copy(T))
    expr = pe(expr) - y
    y_val = eval(str(sp.solve(expr, y)[0]))
    return y_val

######################################################################################################################## calculate_viscosity()
def calculate_viscosity(ln):
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
         omega.append((f_spd0[i] + r_spd0[i] + f_spd1[i] + r_spd1[i] + f_spd2[i] + r_spd2[i]) / 6.0)
    omega   = np.array(omega, np.float64)
    omega   = (omega * 2.0 * np.pi) / 60.0

    current = resx.get_current(cra)
    
    voltage = filt_r(st, Vms)
    omega  = filt_r(st, omega)
    current  = filt_r(st, current)
    
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
    T = resx.cal_TauIemf[0] * (current - current_coil) + resx.cal_TauIemf[1]
    tau    = resx.get_stress(T, 15)
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

def main(s):
    global stdscr
    stdscr = s
    res = 0
    while res != 4:
        try:
            res = menu(res)
        except CAE:
            pass

# if debug: no logging
if debug:
    mparams={'poll_logging':False}
else:
    mparams={'poll_logging':True}


mot = motor(**mparams)
stdscr = 0

curses.wrapper(main)
