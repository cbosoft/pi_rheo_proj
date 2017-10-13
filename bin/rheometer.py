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

## WHILE WE'RE HERE...
## Get size of console and set limits to display
import os
console_height, console_width = os.popen('stty size', 'r').read().split()
draw_width = int(console_width) - 2
draw_height = int(console_height) - 2

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
from filter import filter as filt_r
import dproc
from dproc import fit_line
from dproc import plot_fit
from dproc import read_logf
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

version = dproc.version

class inputs(enum):
    none_   = 1
    enum_   = 2
    string_ = 3

class CAE(Exception):
    '''Handy for easily cancelling out of a deep nest'''
    pass
    
    def __str__(self):
        return "Cancelled"

######################################################################################################################## DISPLAY
def display(blurb, options, selected=0, input_type=inputs.enum_):
    global stdscr
    global debug
    global mot
    stdscr.clear()
    stdscr.border(0)

    # RPi-R header
    mode_string = "[motor off]"
    if mot.ldc: mode_string = "[MOTOR ON]"
    if debug: mode_string = "[DEBUG]"
    
    blurbheight = 0
    
    if draw_height > 30:
        stdscr.addstr(3, 1,  r"            _        _                ".center(draw_width))
        stdscr.addstr(4, 1,  r" _ __ _ __ (_)  _ __| |__   ___  ___  ".center(draw_width))
        stdscr.addstr(5, 1,  r"| '__| '_ \| | | '__| '_ \ / _ \/ _ \ ".center(draw_width))
        stdscr.addstr(6, 1,  r"| |  | |_) | |_| |  | | | |  __/ (_) |".center(draw_width))
        stdscr.addstr(7, 1,  r"|_|  | .__/|_(_)_|  |_| |_|\___|\___/ ".center(draw_width))
        stdscr.addstr(8, 1,  r"     |_| Raspberry Pi Rheometer v{}".format(version).center(draw_width))
        stdscr.addstr(9, 1,  r"".center(draw_width))
        stdscr.addstr(10, 1,  r"{}".format(mode_string.center(draw_width)))

        blurbheight = 12
    else:
        stdscr.addstr(4, 1,  "Raspberry Pi Rheometer v{}".format(version).center(draw_width))
        stdscr.addstr(6, 1,  r"{}".format(mode_string.center(draw_width)))
        blurbheight = 8
    # Display Blurb
    blurboff = 0
    for i in range(0, len(blurb)):
        if (len(blurb[i]) > 0) or draw_height > 30:
            stdscr.addstr(blurbheight + i - blurboff, 1, blurb[i][:draw_width].center(draw_width))
        else:
            blurboff += 1
    
    # Show Options
    for i in range(0, len(options)):
        if (selected == i and input_type == inputs.enum_):
            stdscr.addstr(blurbheight + len(blurb) - blurboff + i + 1, 1, options[i][:draw_width].center(draw_width), curses.A_STANDOUT)
        else:
            stdscr.addstr(blurbheight + len(blurb) - blurboff + i + 1, 1, options[i][:draw_width].center(draw_width))

    # Get Input
    stdscr.addstr(0,0, "")
    stdscr.refresh()
    if input_type == inputs.enum_:
        res = stdscr.getch()
    elif input_type == inputs.string_:
        curses.echo()
        stdscr.addstr(blurbheight + len(blurb) - blurboff + len(options) + 2, 10, "".center(draw_width - 20, "."))
        res = stdscr.getstr(blurbheight + len(blurb) - blurboff + len(options) + 2, 10, (draw_width - 20))
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
        
        if res == 1: raise CAE
        
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
            mot.start_poll(name=cur_log, controlled=False, debug_=debug)
            for i in range(0, len_ccal):
                dc = (100.0 / (len_ccal - 1)) * i
                mot.set_dc(dc)
                width = 40
                
                # Calculate Progress Percentage
                perc = int(math.ceil((i / float(len_ccal)) * width))
                neg_perc = int(math.floor(((float(len_ccal) - i) / len_ccal) * width))
                
                # Calculate speed data
                fspd = np.average(mot.f_speeds)
                rspd = np.average(mot.r_speeds)
                aspd = (fspd + rspd) * 0.5
                aspd_rads = aspd * 2.0 * np.pi / 60.0
                
                # Get motor supply voltage
                vms = mot.volts[7] * dproc.vmsmult
                if vms == 0: vms = 10**-10
                
                # Calculate viscosity from sensor data
                gd = dproc.get_strain(aspd_rads)
                if gd == 0: gd = 10**-10
                ico = dproc.get_current_coil(vms)
                ims = dproc.get_current(mot.volts[2])
                iemf = ims - ico
                T = dproc.T_of_Iemf(iemf)
                tau = dproc.get_stress(T, 15)
                if tau < 0: tau = 0.0
                mu = tau / gd
                
                # Display!
                blurb = [
                        "Current Calibration",
                        "",
                        "{}    {}".format("Electronics".center(38), "Mechanics".center(38)),
                        "{}{}    {}{}".format("Vms:".center(19), "{:.3f} V".format(vms).center(19), "omega:".center(19), "{:.3f} rad/s".format(aspd_rads).center(19)),
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
            Ims = dproc.get_current(cra)
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
             "\tIco = Vms * {} + {}".format(dproc.cal_IcoVms[0], dproc.cal_IcoVms[1]),
             "",
             "New fit:",
             "\tIco = Vms * {} + {}".format(coeffs[0], coeffs[1])]
            options = ["Save results", "Discard"]
            
            res = display(blurb, options)
            
            if res == 0:
                dproc.cal_IcoVms = coeffs
                dproc.writeout()
            
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
        cal_strain = 125
            
        finished = False
        count = 1
            
        while not finished:
            inp_k = False
            ex_inf = ""
            while not inp_k:
                blurb = [   "Motor Calibration: fluid {}".format(count),
                            "",
                            "Fill the cylinder with a reference fluid up to the \"15ml min\" line.",
                            "Then raise the platform so that the liquid level raises to the \"15ml max\" line.",
                            "",
                            "Enter the nominal viscosity (in Pa.s), or enter the name of the fluid, OR enter a",
                            "fluid mixture followed by the composition (weight%)",
                            ex_inf,
                            "e.g. '0.01'",
                            "or 'glycerol'",
                            "or 'glycerol+water@0.45' the characters used here are important! Do not deviate."
                        ]
                options = [" "]
                    
                str_nom_visc = display(blurb, options, input_type=inputs.string_)
                try:
                    ref_viscs.append(float(str_nom_visc))       # assumes is float of nominal viscosity...
                    inp_k = True
                except:
                    try:
                        dproc.get_mu_of_T(str_nom_visc, 25.0)    #   ... or name of species...
                        ref_viscs.append(str_nom_visc)
                        inp_k = True
                    except:
                        try:
                            parts = str_nom_visc.split("@")
                            dproc.get_mu_of_T(parts[0], 25.0, parts[1])
                            ref_viscs.append(str_nom_visc)
                            inp_k = True
                        except:
                            ex_inf = "Couldn't understand... Did you spell it correctly?"
                            inp_k = False
            inp_k = False

            while not inp_k:
                blurb = [   "Motor Calibration: fluid {}".format(count),
                            "",
                            "Enter a name to distinguish this log from the rest:"
                        ]
                options = [" "]
                    
                str_ref_nam = display(blurb, options, input_type=inputs.string_)
                blurb = [   "Motor Calibration: fluid {}".format(count),
                            "",
                            "\"{}\"?".format(str_ref_nam)
                        ]
                options = ["Continue", "Re-enter"]
                    
                rep = display(blurb, options, input_type=inputs.enum_)
                if rep == 0:
                    inp_k = True
                    ref_nams.append(str_ref_nam)
                
            blurb = [   "Motor Calibration: fluid {}".format(count),
                        "",
                        "Now the fluid will be sheared for {} minutes at a strain of ~{} (s^-1).".format(float(cal_len) / 60.0, cal_strain),
                    ]
            options = [ "Continue", "Cancel" ]
                
            res = display(blurb, options)
                
            if res == 1: raise CAE
            
            ref_log = "./../logs/mcal_{}_{}_{}.csv".format(ref_nams[-1], ref_viscs[-1], time.strftime("%d.%m.%y-%H%M", time.gmtime()))
            
            run_test("newt_ref", cal_len, 125, title="Reference {} Test: {}".format(count, ref_nams[-1]), ln_override=ref_log)
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
        
        mot_cal(ref_logs)
    else:
        return 4
    return 1

######################################################################################################################## mot_cal()
def mot_cal(ref_logs):
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
        
        # mcal_[name]_[viscosity]_[date+time].csv
        v_term = ref_logs[i].split('_')[2]
        try:
            viscosity = float(v_term) # if is any of the 'smart' options, this will not work
        except:
            try:
                viscosity = dproc.get_mu_of_T(v_term, T) # will not work if is mixture
            except:
                parts = v_term.split("@")
                viscosity = dproc.get_mu_of_T(parts[0], T, parts[1]) # will not work if something has gone wrong
                                                                    # errors should have been caught earlier
        
        I_MS = dproc.get_current(cra)
        I_CO = dproc.get_current_coil(Vms)
        I_EMF = [0.0] * len(I_MS)
        display(["{}  {}  {}".format(len(I_MS), len(I_CO), len(I_EMF))], [], input_type=inputs.none_)
        for j in range(0, len(I_MS)):
            I_EMF[j] = I_MS[j] - I_CO[j]
        I_EMFs.append(np.average(I_EMF))
                
        stress = viscosity * np.average(gamma_dot) # pa = pa.s * (1/s)
        torque = dproc.get_torque(stress, 15)
        T_MSs.append(torque)
            
    __, f_eqn, mot_cal = plot_fit(I_EMFs, np.log(T_MSs), 1, x_name="Iemf", y_name="T", outp="./../plots/cal_mot.png")
        
    blurb = ["Motor Calibration",
             "",
             "Complete! Plot saved as \"./../plots/cal_mot.png\"",
             "",
             "Previous fit:",
             "\tT = Iemf * {} + {}".format(dproc.cal_TIemf[0], dproc.cal_TIemf[1]),
             "",
             "New fit:",
             "\tT = Iemf * {} + {}".format(mot_cal[0], mot_cal[1])]
    options = ["Save results", "Discard"]
            
    res = display(blurb, options)
            
    if res == 0:
        dproc.cal_TIemf = mot_cal
        dproc.writeout()
    
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
                        "{}{}    {}{}".format("".center(19), "".center(19), "tau:".center(19), "-- Pa".center(19)),
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

    mot.start_poll(name=ln, controlled=True, debug_=debug)
    
    for i in range(0, length):
        gd_expr = str(gd_expr)
        gd = sp.Symbol('gd')
        t = float(copy.copy(i))
        expr = pe(gd_expr) - gd
        gd_val = eval(str(sp.solve(expr, gd)[0]))
        set_strain_rate(gd_val)
        
        ## Progress bar
        width = 40
        perc = int(math.ceil((i / float(length)) * width))
        neg_perc = int(math.floor(((float(length) - i) / length) * width))
        
        ## Status
        fspd = np.average(mot.f_speeds)
        rspd = np.average(mot.r_speeds)
        aspd = (fspd + rspd) * 0.5
        aspd_rads = (aspd * 2 * np.pi) / 60.0
        dc   = mot.ldc
        vms  = mot.volts[7] * dproc.vmsmult
        ims  = dproc.get_current(mot.volts[2])
        gd, __, tau, mu = dproc.calc_mu(1, vms, ims, 15, aspd_rads, dwdt_override=0)
        blurb = [
                title,
                "",
                "{}    {}".format("Electronics".center(38), "Mechanics".center(38)),
                "{}{}    {}{}".format("Vms:".center(19), "{:.3f} V".format(vms).center(19), "omega:".center(19), "{:.3f} rad/s".format(aspd_rads).center(19)),
                "{}{}    {}{}".format("Ims:".center(19), "{:.3f} A".format(ims).center(19), "gamma dot:".center(19), "{:.3f} (s^-1)".format(gd).center(19)),
                "{}{}    {}{}".format("".center(19), "".center(19), "tau:".center(19), "{} Pa".format(tau).center(19)),
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
    '''
    __, st, __, omega_rads, __, __, __, __, Ims, __, __, __, Vms, __, __, __ = read_logf(ln, dia=True)
    gamma_dot, T, tau, mu = dproc.calc_mu(st, Vms, Ims, 15, omega_rads)
    
    logf = open("{}_results.csv".format(ln[:-4]), "w")
    logf.write("st,omega_rads,Ims,Vms,gamma_dot,T,tau,mu\n")
    for i in range(0, len(st)):
        line = "{},{},{},{},{},{},{},{}\n".format(st[i]. omega_rads[i],Ims[i],Vms[i],gamma_dot[i],T[i],tau[i],mu[i])
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
if False:#debug:
    mparams={'poll_logging':False}
else:
    mparams={'poll_logging':True}


mot = motor()#**mparams)
stdscr = 0

curses.wrapper(main)
