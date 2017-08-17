#
# rheometer.py
#
# class object controlling the rheometer from the rasbperry pi
#

debug = False

packages_missing = [""]
print "Loading packages.."

## Included in python...
print "\nPackages Included in Python2.7+\n"
print "\ttime"  #           (for telling the time)"
import time
print "\tsys"  #            (to read arguments passed to the script)"
import sys
print "\tmath"  #           (to do simple maths)"
import math
from math import sin
from math import cos
print "\tcopy"  #           (to make proper copies of variables)"
import copy
print "\trandom"  #         (to generate random numbers)"
import random
print "\tglob.glob"  #      (to search for files)"
from glob import glob
print "\tplatform"  #       (to check what os this is on)"
import platform

## Third party
print "\n3rd Party Packages\n"
print "\tnumpy"  #          (to do cool things with arrays, and other maths)"
try:
    import numpy as np
except ImportError as ex:
    packages_missing.append("pipnumpy")
    print "\t !! error !!"
    
print "\tpandas"  #         (to read .csv files easily)"
try:
    import pandas as pd
except ImportError as ex:
    packages_missing.append("pippandas")
    print "\t !! error !!"
    
print "\tcurses"  #         (to display things nicely)"
try:
    import curses
except ImportError as ex:
    packages_missing.append("pipcurses")
    print "\t !! error !!"
    
print "\tmatplotlib"  #     (to plot information)"
try:
    import matplotlib
except ImportError as ex:
    packages_missing.append("pipmatplotlib")
    print "\t !! error !!"
    
print "\tSymPy"  #          (to solve functions symbolically)"
try:
    from sympy.parsing.sympy_parser import parse_expr as pe
    import sympy as sp
except ImportError as ex:
    packages_missing.append("pipsympy")
    print "\t !! error !!"
    
print "\tpython-tk"  #      (fixes a bug I think...)"
try:
    import _tkinter
except ImportError as ex:
    packages_missing.append("aptpython-tk")
    print "\t !! error !!"
    
print "\tspidev"  #         (to communicate over SPI with hardware)
try:
    import spidev
except:
    debug = True
    print "\t inactive !!"
    
## RPi-Rheo packages
print "\nRPi-Rheo Packages\n"
print "\tresx.py"  #        (to read/save calibration and other misc data)"
import resx

print "\tfilter.py"  #      (digital signal filtering wrapper for scipy)"
from filter import filter

print "\tplot_help.py"  #   (easy reading of logs)"
from plothelp import fit_line
from plothelp import read_logf
from plothelp import simple_get_results
    
print "\tmotor.py"  #       (allows control of motor)"
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

if dist == "Raspbian": debug = True

if debug: print "\tDEBUG MODE !!"

if len(packages_missing) > 1: 
    print ""
    print "!! -- Packages missing -- !!"
    exit()

version = resx.version

class rheometer(object):
    
    # geometry
    roo = resx.ocor                 # outer cell outer radius in m
    ro = resx.ocir                  # outer cell radius in m
    ri = resx.icor                  # inner cell radius in m
    icxsa   = np.pi * (ri ** 2)     # inner cylinder XSA
    ocxsa   = np.pi * (ro ** 2)     # outer cylinder XSA
    dxsa    = ocxsa - icxsa         # vol per height in m3/m
    dxsa    = dxsa * 1000           # l / m
    dxsa    = dxsa * 1000           # ml / m
    fill_height = 0
    
    # empirical calibrations
    dynamo_cal = resx.cal_dynamo #[312.806, -159.196]
    hes30A_cal = resx.cal_30AHES
    hes5A_cal = resx.cal_5AHES
    
    # classes
    mot = motor()
    
    # vars
    motor_running = False
    
    def __init__(self, motor_params={'log_dir':'./logs'}):
        #print "Initialising motor..."
        self.mot = motor(**motor_params)
    
    #################################################################################################################### DISPLAY
    def display(self, blurb, options, selected=0, get_input=True, input_type="enum"):
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
            if (selected == i and input_type != "string" and get_input):
                stdscr.addstr(blurbheight + len(blurb) + i + 1, 1, options[i].center(80), curses.A_STANDOUT)
            else:
                stdscr.addstr(blurbheight + len(blurb) + i + 1, 1, options[i].center(80))

        # Get Input
        stdscr.addstr(0,0, "")
        stdscr.refresh()
        if get_input and input_type == "enum":
            res = stdscr.getch()
        elif get_input and input_type == "string":
            curses.echo()
            stdscr.addstr(blurbheight + len(blurb) + len(options) + 2, 10, "".center(60, "."))
            res = stdscr.getstr(blurbheight + len(blurb) + len(options) + 2, 10, 60)
        else:
            res = 10

        # Return
        if input_type == "string":
            curses.noecho()
        elif res == curses.KEY_UP:
            # up arrow, reduce selection
            if selected == 0:
                selected = len(options) - 1
            else:
                selected -= 1
                
            res = self.display(blurb, options, selected, True)
        elif res == curses.KEY_DOWN:
            # down arrow, increase selection
            if selected == len(options) - 1:
                selected = 0
            else:
                selected += 1

            res = self.display(blurb, options, selected, True)
        elif res == curses.KEY_ENTER or res == 10 or res == 13:
            res = selected
        else:
            res = self.display(blurb, options, selected, True)
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
                
                length = self.display(blurb, options, get_input=True, input_type="string")
                
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
                         "Note:",
                         "Minimum value =   5 (s^-1)",
                         "Maximum value = 250 (s^-1)"]
                options = [""]
                
                gd_expr = self.display(blurb, options, get_input=True, input_type="string")
                
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
                
                tag = self.display(blurb, options, get_input=True, input_type="string")
                
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
            
            length = 0
            res = "car"
            not_okay = True
            while not_okay:
                blurb = [   "To calibrate the sensors, allow the inner cylinder to freely rotate.",
                            "Ensure there is nothing impacting on the rotation of the cylinder, nothing touching it",
                            "",
                            "A run of data-logging is used to calibrate the sensor.",
                            "Running for at least ten minutes (600s) is recommended to gather enough information.",
                            "",
                            "Enter the desired length of data-run (in seconds):"]
                options = list()
                res = self.display(blurb, options, input_type="string", get_input=True)
                
                try:
                    length = int(res)
                    not_okay = False
                except:
                    not_okay = True
            
            stay = length / 17
            
            blurb = [   "The motor's voltage will be varied between minimum (2.422v) and ",
                        "maximum (10.87v).",
                        "",
                        "This will be steadily varied over the course of {}s".format((17 * stay))]
            options = [ "Continue",
                        "Cancel"    ]
            
            res = self.display(blurb, options, get_input=True, input_type="enum")
            
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
                                "Sensor Calibration", 
                                "", #cp:{}  oo:{} st:{}".format(cur_po, out_of, stay),
                                "{}{}".format("Value sent to potentiometer:".center(40), str(self.mot.pot.lav).center(40)),
                                "{}{}".format("Time remaining:".center(40), "{}s".format(int(out_of - cur_po)).center(40)),
                                "",
                                "[{}{}]".format("#" * perc, " " * neg_perc).center(60)
                                ]
                        options = [" "]
                        self.display(blurb, options, get_input=False)
                        cycle_motor()
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
                
                res = self.display(blurb, options, True, input_type="enum")
                
                if res == 0:
                    # accept the new calibrations
                    resx.cal_dynamo = dr
                    resx.cal_30AHES = cr
                    resx.cal_5AHES = cr2
                    
                    resx.writeout()
                    
                    self.display(["New calibrations set (saved in \"./../etc/data.xml\")!"], ["Continue"], 
                                 True, input_type="enum")
                
            
        elif res == 2: ################################################################################################# OVERCAL: 2
            # Calibration Override
            blurb = [   "If the current calibration is not useful, it can be rolled back to a previous version",
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
                
                self.display(blurb, options, get_input=True, input_type="enum")
            else:
                res = self.display(blurb, options, get_input=True, input_type="enum")
                
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
                
                res = self.display(blurb, options, True, input_type="enum")
                
                if res == 0:
                    # accept the new calibrations
                    resx.cal_dynamo = dr
                    resx.cal_30AHES = cr
                    resx.cal_5AHES = cr2
                    
                    resx.writeout()
                    
                    self.display(["New calibrations set (saved in \"./../etc/data.xml\")!"], ["Continue"], 
                                 True, input_type="enum")
            
        elif res == 3: ################################################################################################# README: 3
            # View readme/manual
            blurb = ["RPi-R: Simple rheometry indicator",
                     " ",
                     "Power into the motor to maintain a set strain rate",
                     "is related to the viscosity of the fluid in the cell.",
                     "",
                     "An unknown fluid can be characterised by comparing",
                     "the power draw of the loadless cell to the draw of the",
                     "loaded cell."]
            options = ["Continue"]
            
            self.display(blurb, options)
        else:
            return 4
        return 1
            
    #################################################################################################################### run_test()
    def run_test(self, tag, length, gd_expr):
        self.display(["Rheometry Test", "", ""],[""], get_input=False)
        ln = "./../logs/rheometry_test_{}_{}.csv".format(tag, time.strftime("%d%m%y_%H%M", time.gmtime()))
        
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
                    "Rheometry Test",
                    "",
                    "{}{}".format("Supply voltage set to:".center(40), "{:.3f} V".format(vms).center(40)),
                    "{}{}".format("Target strain rate:".center(40), "{:.3f} (s^-1)".format(gd_val).center(40)),
                    "{}{}".format("Value sent to potentiometer:".center(40), str(self.mot.pot.lav).center(40)),
                    "{}{}".format("Time remaining:".center(40), "{}s".format(length - i).center(40)),
                    "",
                    "[{}{}]".format("#" * perc, " " * neg_perc)
                    ]
            options = [" "]
            self.display(blurb, options, get_input=False)
            time.sleep(1)
        
        self.mot.clean_exit()
        return ln
       
    #################################################################################################################### set_strain_rate()   
    def set_strain_rate(self, value):
        desired_speed = value * (self.ro - self.ri) / self.ri  # in rads
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
            crf = filter(st, cr, method="butter", A=2, B=0.001)
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
        if filteron: cra     = filter(st, cra, method="butter", A=2, B=0.001)

        st      = range(0, len(crb))
        if filteron: crb     = filter(st, crb, method="butter", A=2, B=0.001)

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
        __, st, dr, cr, cr2a, cr2b, pv, __, __, __, __, __, __, __, __ = read_logf(log_file_name)
        
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
        
        return dr_cal, cr_cal, cr2_cal
    
    #################################################################################################################### cycle_motor()
    def cycle_motor(self, show_screen=False):
        
        # display wait screen
        blurb = [" ", " Cycling motor..."]
        options = [" "]
        if show_screen: self.display(blurb, options, get_input=False)
        
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
        self.motor_running = value
        if value:
            self.mot.actuate()
        else:
            self.mot.deactuate()
        
if __name__ == "__main__":
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
