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
    
    # classes
    mot = motor()
    
    # vars
    motor_running = False
    
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
        if self.motor_running: mode_string = "!! MOTOR ON !!"
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
                    "Welcome to RPi-R: Simple rheometry recording with a Raspberry Pi",
                    ]
        options =   [
                    "Run test",                     # 0
                    "Re-calibrate sensors",         # 1
                    "Override Latest Calibration",  # 2
                    "View Readme",                  # 3
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
            # As calibration override, but with 10 minute run before hand
            
            ### Part 1: Sensor Calibration ###
            
            length = 0
            res = "car"
            not_okay = True
            while not_okay:
                blurb = [   "Calibration 1",
                            "",
                            "To calibrate the sensors, allow the inner cylinder to freely rotate.",
                            "Ensure there is nothing impacting on the rotation of the cylinder, nothing touching it",
                            "",
                            "A run of data-logging is used to calibrate the sensor.",
                            "Running for at least ten minutes (600s) is recommended to gather enough information.",
                            "",
                            "Enter the desired length of data-run (in seconds):"]
                options = list()
                res = self.display(blurb, options, input_type=inputs.string_)
                
                try:
                    length = int(res)
                    not_okay = False
                except:
                    not_okay = True
            
            stay = length / 17
            
            blurb = [   "Calibration 1",
                        "",
                        "The motor's voltage will be varied between minimum (2.422v) and ",
                        "maximum (10.87v).",
                        "",
                        "This will be steadily varied over the course of {}s".format((17 * stay))]
            options = [ "Continue",
                        "Cancel"    ]
            
            res = self.display(blurb, options)
            
            if res == 0:
                ln = "./../logs/sensor_calibration_{}.csv".format(time.strftime("%d%m%y_%H%M", time.gmtime()))
                
                if not debug:
                    self.mot.start_poll(ln)
                else:
                    ln = sorted(glob("./../logs/sensor_*"))[-1] #if debug, use latest sensor calibration
                
                for pv in range(0, 17):
                    for i in range(0, stay):
                        self.mot.set_pot(i)
                        
                        out_of = 17.0 * stay
                        cur_po = (pv * stay) + i
                        
                        vms = 0.066 * self.mot.pot.lav + 2.422
                        width = 60
                        
                        perc = int(math.ceil((cur_po / out_of) * width))
                        
                        neg_perc = int(math.floor(((out_of - cur_po) / out_of) * width))
                        
                        blurb = [
                                "Calibration 1", 
                                "", #cp:{}  oo:{} st:{}".format(cur_po, out_of, stay),
                                "{}{}".format("Value sent to potentiometer:".center(40), str(self.mot.pot.lav).center(40)),
                                "{}{}".format("Time remaining:".center(40), "{}s".format(int(out_of - cur_po)).center(40)),
                                "",
                                "[{}{}]".format("#" * perc, " " * neg_perc).center(60)
                                ]
                        options = [" "]
                        self.display(blurb, options, input_type=inputs.none_)
                        self.cycle_motor()
                        time.sleep(1)
                        
                if not debug: self.mot.clean_exit()
                
                # calculate calibrations
                dr, cr, cr2 = self.calculate_calibrations(ln)
                
                blurb = [   "The data-run was saved in \"{}\"".format(options[res]),
                            "",
                            "Calibrations calculated from this log:",
                            "",
                            "{}{}".format("Dynamo".center(40), "{} Vdr + {}".format(dr[0], dr[1]).center(40)),
                            "{}{}".format("30A HES".center(40), "{} Vcr + {}".format(cr[0], cr[1]).center(40)),
                            "{}{}".format("5AHES".center(40), "{} Vcr2 + {}".format(cr2[0], cr2[1]).center(40)) ]
                
                options = [ "Accept Calibrations", "Cancel"]
                
                res = self.display(blurb, options)
                
                if res == 0:
                    # accept the new calibrations
                    resx.cal_dynamo = dr
                    resx.cal_30AHES = cr
                    resx.cal_5AHES = cr2
                    
                    resx.writeout()
                    
                    self.display(["New calibrations set (saved in \"./../etc/data.xml\")!"], ["Continue"])
                
                ### Part 2: Motor Calibration ###
                blurb = [   "Calibration 2",
                            "",
                            "The torque output of the motor will be related to the current it draws.",
                            "Required are at least two newtonian reference fluids of known viscosity."
                        ]
                options = [ "Continue", "Cancel" ]
                
                res = self.display(blurb, options)
                
                if res == 1: x = 1 + "t"  # cancelations are exceptional
                
                ref_logs  = list()
                ref_viscs = list()
                
                finished = False
                count = 1
                inp_k = False
                
                while not finished:
                    while not inp_k:
                        blurb = [   "Calibration 2: fluid {}".format(count),
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
                    
                    blurb = [   "Calibration 2: fluid {}".format(count),
                                "",
                                "Now the fluid will be run for 10 minutes at a strain rate of ~125 (s^-1).",
                            ]
                    options = [ "Continue", "Cancel" ]
                    
                    res = self.display(blurb, options)
                    
                    if res == 1: x = 1 + "t"
                    
                    ref_log = self.run_test("newt_ref_1", 600, 125, title="Reference 1 Test", ln_prefix="motor_calibration")
                    ref_logs.append(ref_log)
                    
                    count += 1
                    
                    if count == 2:
                        finished = False
                    else: # count > 2
                        blurb = [   "Calibration 2: fluid {}".format(count - 1),
                                    "",
                                    "Do you wish to use further reference fluids? ({} so far)".format(count - 1) ]
                        options = ["Yes", "No"]
                        res = self.display(blurb, options)
                        
                        if res == 1: finished = True
                            
                blurb = [ "Calibration 2",
                          "",
                          "Calculating..." ]

                self.display(blurb, list(), input_type=inputs.none_)
                
                I_EMFs = list()
                T_MSs  = list()
                
                for i in range(0, len(ref_logs)):
                    __, st, dr, cr, cr2a, cr2b, pv, T, Vpz, gamma_dot, tau, tag = read_logf(ref_logs[i])
                    
                    I_MS = resx.get_current(cr, cr2a, cr2b)
                    I_CO = resx.get_current_coil(pv)
                    I_EMF = [] * len(I_MS)
                    for j in range(0, len(I_MS)):
                        I_EMF[j] = I_MS[j] - I_CO[j]
                    I_EMFs.append(np.average(I_EMF))
                    
                    stress = ref_viscs[i] * np.average(gamma_dot)
                    torque = resx.get_torque(stress, 15)
                    T_MSs.append(np.average(torque))
                
                __, f_eqn, mot_cal = fit_line(I_EMFs, T_MSs, 1)
                
                blurb = ["Calibration 2",
                         "",
                         "Complete!",
                         "",
                         "Resulting fit:",
                         "\t{}".format(f_eqn)]
                options = ["Save results", "Discard"]
                
                res = self.display(blurb, options)
                
                if res == 0:
                    resx.cal_TauIemf = mot_cal
                    resx.writeout()
            
        elif res == 2: ################################################################################################# OVERCAL: 2
            # Calibration Override
            blurb = [   "If the current sensor calibrations are not useful, they can be rolled back.",
                        "",
                        "Choose from the versions below:" ]
            
            #load previous versions from log file with prefix "sensor_calibration_"
            
            options = sorted(glob("./../logs/sensor_calibration_*"))
            
            if len(options) > 5: options = options[-5:]
            
            if len(options) < 1:
                blurb = [   "There are no sensor logs to use!",
                            "",
                            "Run a calibration from the main menu." ]
                            
                options = [ "Continue"]
                
                self.display(blurb, options)
            else:
                res = self.display(blurb, options)
                
                # calculate calibrations
                dr, cr, cr2 = self.calculate_calibrations(options[res])
                
                blurb = [   "The log file \"{}\" was selected".format(options[res]),
                            "",
                            "Calibrations calculated from this log:",
                            "",
                            "{}{}".format("Dynamo".center(40), "{} Vdr + {}".format(dr[0], dr[1]).center(40)),
                            "{}{}".format("30A HES".center(40), "{} Vcr + {}".format(cr[0], cr[1]).center(40)),
                            "{}{}".format("5AHES".center(40), "{} Vcr2 + {}".format(cr2[0], cr2[1]).center(40)) ]
                
                options = [ "Accept Calibrations", "Cancel"]
                
                res = self.display(blurb, options)
                
                if res == 0:
                    # accept the new calibrations
                    resx.cal_dynamo = dr
                    resx.cal_30AHES = cr
                    resx.cal_5AHES = cr2
                    
                    resx.writeout()
                    
                    self.display(["New calibrations set (saved in \"./../etc/data.xml\")!"], ["Continue"])
            
        elif res == 3: ################################################################################################# README: 3
            # View readme/manual
            blurb = ["RPi-R: Simple rheometry indicator",
                     " ",
                     "Nothing here I'm afraid.",
                     "",
                     "Probably a good idea to look at the individual .py files",
                     "if you want to know how this works."]
            options = ["Continue"]
            
            self.display(blurb, options)
        else:
            return 4
        return 1
            
    #################################################################################################################### run_test()
    def run_test(self, tag, length, gd_expr, title="Rheometry Test", ln_prefix="rheometry_test"):
        gd_expr = str(gd_expr)
        self.display([title, "", ""], [""], input_type=inputs.none_)
        ln = "./../logs/{}_{}_{}.csv".format(ln_prefix, tag, time.strftime("%d%m%y_%H%M", time.gmtime()))
        
        #recrdr = rec.recorder()
        #recrdr.start_recording(ln[:-3] + "wav")
        
        if not debug: self.mot.start_poll(ln)
        
        gd = sp.Symbol('gd')
        
        for i in range(0, length):
            t = float(copy.copy(i))
            
            expr = pe(gd_expr) - gd
            
            gd_val = eval(str(sp.solve(expr, gd)[0]))
            
            #self.mot.set_pot(gd_val)
            self.set_strain_rate(gd_val)
            
            vms = 0.066 * self.mot.pot.lav + 2.422
            width = 40
            perc = int(math.ceil((i / float(length)) * width))
            neg_perc = int(math.floor(((float(length) - i) / length) * width))
            blurb = [
                    title,
                    "",
                    "{}{}".format("Supply voltage set to:".center(40), "{:.3f} V".format(vms).center(40)),
                    "{}{}".format("Target strain rate:".center(40), "{:.3f} (s^-1)".format(gd_val).center(40)),
                    "{}{}".format("Value sent to potentiometer:".center(40), str(self.mot.pot.lav).center(40)),
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
            pass#self.calculate_viscosity(ln)
        
        blurb = [
                title,
                "",
                "Processing complete!" ]
        
        options = [" "]
        self.display(blurb, options, input_type=inputs.none_)
        
        return ln
       
    #################################################################################################################### set_strain_rate()   
    def set_strain_rate(self, value):
        desired_speed = value * (resx.ocir - resx.icor) / resx.icor  # in rads
        desired_speed = desired_speed * 60 / (2 * np.pi)  # in rpms
        if self.mot.control_stopped:
            set_pv = int((desired_speed - resx.cal_Vnl[1]) / resx.cal_Vnl[0])
            self.mot.set_pot(set_pv)
        else:
            self.mot.update_setpoint(desired_speed)

    #################################################################################################################### cal_30ahes(self, cr, vms, cua, filteron=False)
    def cal_30ahes(self, cr, vms, cua, filteron=False):
        st  = range(0, len(cr))
        if filteron: 
            crf = filt_r(st, cr)
        else:
            crf = cr
        cu  = [0] * 0

        # From ammeter
        for v in vms:
            cu.append(cua[v])

        # Form trendline: CRF vs CU
        coeffs = np.polyfit(crf, cu, 1)
        return coeffs
    
    #################################################################################################################### cal_5ahes(self, cra, crb, vms, cua, filteron=False)
    def cal_5ahes(self, cra, crb, vms, cua, filteron=False):
        st      = range(0, len(cra))
        if filteron: cra     = filt_r(st, cra)

        st      = range(0, len(crb))
        if filteron: crb     = filt_r(st, crb)

        crf     = 0.5 * (cra + crb)
        cu      = [0] * 0

        # From ammeter
        for v in vms:
            cu.append(cua[v])

        # Form trendline: CRF vs CU
        coeffs = np.polyfit(crf, cu, 1)
        return coeffs
    
    #################################################################################################################### cal_dynamo(self, dr, vms)
    def cal_dynamo(self, dr, vms):
        # Read csv
        datf    = pd.read_csv("./../logs/main_speed_v_vms.csv")

        vmsm    = np.array(datf['vms'], np.float64)
        spd1    = np.array(datf['spd1'], np.float64)
        spd2    = np.array(datf['spd2'], np.float64)
        spd3    = np.array(datf['spd3'], np.float64)

        av_spd  = (spd1 + spd2 + spd3) / 3

        vdict = dict()
        for i in range(0, len(vmsm)):
            vdict[str(vmsm[i])] = av_spd[i] # returns speed value for voltage key
        
        allowed_vms = list()
        for i in range(0, 17):
            allowed_vms.append((0.066 * 8 * i) + 2.422)
        
        spd_long = list()
        dr_long = list()
        is_allowed = False
        for i in range(0, len(vms)):
            for a_v in allowed_vms:
                if vms[i] == a_v: 
                    spd_long.append(vdict[str(vms[i])])
                    dr_long.append(dr[i])
 
        coeffs = np.polyfit(dr_long, spd_long, 1)
        return coeffs

    #################################################################################################################### calculate_calibrations(self, log_file_name)    
    def calculate_calibrations(self, log_file_name):
        __, st, dr, cr, cr2a, cr2b, pv, __, __, __, __, __ = read_logf(log_file_name)
        
        vms = (0.066 * pv) + 2.422      # This voltage function originates from an old prophecy,
                                        # foretold by the oracles in the days of MEng.
        
        cua = dict()
        for i in range(0, len(vms)):
            cua[vms[i]] = (0.02948 * vms[i]) + 0.4506   # The same prophecy spoke also of
                                                        # a further function.. one to predict
                                                        # the ampere pull of a motor....
        
        
        dr_cal = self.cal_dynamo(dr, vms)
        cr_cal = self.cal_30ahes(cr, vms, cua)
        cr2_cal = self.cal_5ahes(cr2a, cr2b, vms, cua)
        
        return dr_cal, cr_cal, cr2_cal  # HAIL KFB, HAIL THE PROPHET!
    
    #################################################################################################################### cycle_motor()
    def cycle_motor(self, show_screen=False):
        
        # display wait screen
        blurb = [" ", " Cycling motor..."]
        options = [" "]
        if show_screen: self.display(blurb, options, input_type=inputs.none_)
        
        # save PV
        prev_pv = copy.copy(self.mot.pot.lav)

        # get random number
        r = random.randint(1, 2)
        highfirst = True
        # use random to randomise order
        if r == 1: highfirst = False
        
        # set to 4 random PVs
        for i in range(0, 4):
            self.mot.set_pot(random.randint(0, 128))
            time.sleep(0.1)
            
        # set either to highest or lowest
        if highfirst:
            self.mot.set_pot(128)
            time.sleep(0.1)
        else:
            self.mot.set_pot(0)
            time.sleep(0.1)
            
        # another 4 random PVs
        for i in range(0, 4):
            self.mot.set_pot(random.randint(0, 128))
            time.sleep(0.1)
        
        # set to either lowest, or highest
        if not highfirst:
            self.mot.set_pot(128)
            time.sleep(0.1)
        else:
            self.mot.set_pot(0)
            time.sleep(0.1)
        
        # return to original PV
        self.mot.set_pot(prev_pv)
            
    #################################################################################################################### set_relay()
    def set_relay(self, value):
        '''
        set_relay(value)
        
        simply activates or de-activates the motor-controlling 
        relay depending on the [VALUE]. True for activating (thus
        turning on the motor) and false for de-activating (turning
        off the motor).
        '''
        self.motor_running = value
        if value:
            self.mot.actuate()
        else:
            self.mot.deactuate()
    
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
        t, st, dr, cr, cr2a, cr2b, pv, T, Vpz, __, __, tag = read_logf(ln)
        
        # Energy balance method calculation
        omega   = resx.get_speed_rads(dr)
        current = resx.get_current(cr, cr2a, cr2b)
        voltage = resx.get_supply_voltage(pv)
        
        omega   = filt_r(st, omega)
        current = filt_r(st, omega)
        
        ################################################################################
        # Strain rate. #################################################################
        
        gamma_dot = omega * (resx.icor / (resx.ocir - resx.icor)) 
        
        ################################################################################
        # Energy balance. ##############################################################
        
        efficiency = 0.8
        tau       = (efficiency * current * voltage) / omega  
        mu_energy_balance_method = tau / gamma_dot
        
        ################################################################################
        # Current relation. ############################################################
        
        current_coil = resx.get_current_coil(pv)
        tau = resx.cal_TauIemf[0] * (current - current_coil) + resx.cal_TauIemf[1]
        mu_current_relation = tau / gamma_dot
        
        ################################################################################
        # Updating log. ################################################################
        
        logf = open(ln, "w")
        logf.write("t,dr,cr,cr2a,cr2b,pv,T,Vpz,gamma_dot,tau,mu_en_bal,mu_current_relation\n")
        for i in range(0, len(t)):
            line = "{},{},{},{},{},{},{},{},{},{},{},{}\n".format(t[i], dr[i], cr[i], cr2a[i], cr2b[i], pv[i], T[i], Vpz[i], gamma_dot[i], tau[i], mu_energy_balance_method[i], mu_current_relation[i])
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
        mparams={'log_dir':'.','poll_logging':False}
    else:
        mparams={'log_dir':'.','poll_logging':True}

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
