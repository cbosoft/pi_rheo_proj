#
# rheometer.py
#
# class object controlling the rheometer from the rasbperry pi
#


# =============================================== <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# TODO: plot results
# =============================================== <<<<<<<<<<<<<<<<<<<<<<<<<<<<<

packages_missing = [""]
print "Loading packages.."
try:
    print "\ttime"
    import time
except ImportError as ex:
    packages_missing.append("crttime")
try:
    print "\tnumpy"
    import numpy as np
except ImportError as ex:
    packages_missing.append("pipnumpy")
try:
    print "\tpandas"
    import pandas as pd
except ImportError as ex:
    packages_missing.append("pippandas")
try:
    print "\tresources"
    import resx
except ImportError as ex:
    packages_missing.append("crtresx.py")
try:
    print "\tsys"
    import sys
except ImportError as ex:
    packages_missing.append("crtsys")
try:
    print "\tcurses"
    import curses
except ImportError as ex:
    packages_missing.append("pipcurses")
try:
    print "\tmath"
    import math
except ImportError as ex:
    packages_missing.append("crtmath")
try:
    print "\tcopy"
    import copy
except ImportError as ex:
    packages_missing.append("crtcopy")
try:
    print "\tos"
    import os
except ImportError as ex:
    packages_missing.append("crtos")
try:
    print "\trandom"
    import random
except ImportError as ex:
    packages_missing.append("crtrandom")
try:
    print "\tglob.glob"
    from glob import glob
except ImportError as ex:
    packages_missing.append("crtglob")
try:
    print "\tmatplotlib"
    import matplotlib
except ImportError as ex:
    packages_missing.append("pipmatplotlib")
try:
    print "\tSymPy"
    from sympy.parsing.sympy_parser import parse_expr as pe
    import sympy as sp
except ImportError as ex:
    packages_missing.append("pipsympy")
try:
    print "\tpython-tk"
    import _tkinter
except ImportError as ex:
    packages_missing.append("aptpython-tk")
    
if len(packages_missing) > 1: 
    print "!! -- Packages missing -- !!"
    for i in range(1, len(packages_missing)): 
        print "\t" + packages_missing[i][3:]
    print "Automatically trying to obtain missing packages...\n"
    for i in range(1, len(packages_missing)):
        if packages_missing[i][:3] == "apt":
            os.system("sudo apt-get install {}".format(packages_missing[i][3:]))
        elif packages_missing[i][:3] == "pip":
            os.system("sudo -H pip install {}".format(packages_missing[i][3:]))

crit_fail = False
for p in packages_missing:
    if p[:3] == "crt":
        crit_fail = True

if crit_fail:
    print "Some packages could not be automatically installed:\n"
    for p in packages_missing:
        print "\t{}".format(p[3:])
    print "\nIs there a typo in the rheometer script? Broken python install?"
    print "Press any key to continue"
    raw_input()
    exit()

print "\tmotor.py"
from motor import motor

print "\tfilter.py"
from filter import filter

print "\tplot_help.py"
from plothelp import fit_line
from plothelp import read_logf
from plothelp import simple_get_results

try:
    import spidev
except:
    debug = True
else:
    debug = False

    
version = resx.version          # maj.typ.min
                                # MAJOR: Indicates release version
                                # TYPE: What type of release? 
                                #   0: LTS
                                #   1: pre-alpha development
                                #   2: alpha
                                #   3: beta
                                # MINOR: Indicates progress through release (towards next version)


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
        print "Initialising motor..."
        self.mot = motor(**motor_params)
            
    def get_rheometry(self, strain_rate, run_length):
        pass
    
    def display(self, blurb, options, selected=0, get_input=True, options_help="NONE", input_type="enum"):
        
        summ_str = "Update screen:\n\t"
        summ_str += "{}...\n\t".format(blurb[0])
        if get_input:
            summ_str += "Input: "
            if input_type == "enum":
                summ_str += "listed choice"
            else:
                summ_str += "input data"
        else:
            summ_str += "No input taken"
        print summ_str
        
        global stdscr
        global debug
        stdscr.clear()
        stdscr.border(0)
        if options_help == "NONE": options_help = [""] * len(options)

        # RPi-R header
        mode_string = " "
        motor_string = "   MOTOR OFF"
        if self.motor_running: motor_string = "!! MOTOR ON !!"
        if debug: 
            mode_string = "  !! DEBUG !!"
            motor_string = " "
            
        stdscr.addstr(3, 3,  r"____________ _       ______        ")
        stdscr.addstr(4, 3,  r"| ___ \ ___ (_)      | ___ \                {}".format(mode_string))
        stdscr.addstr(5, 3,  r"| |_/ / |_/ /_ ______| |_/ /       ")
        stdscr.addstr(6, 3,  r"|    /|  __/| |______|    /                 ")
        stdscr.addstr(7, 3,  r"| |\ \| |   | |      | |\ \        ")
        stdscr.addstr(8, 3,  r"\_| \_\_|   |_|      \_| \_|       Raspberry Pi Rheometer    v{}".format(version))
        stdscr.addstr(10, 3, r"_____________________________________________________________________")

        blurbheight = 12

        # Display Blurb
        for i in range(0, len(blurb)):
            stdscr.addstr(blurbheight + i, 3, blurb[i])
        
        # Show Options
        for i in range(0, len(options)):
            if selected == i:
                stdscr.addstr(blurbheight + len(blurb) + i + 1, 3, options[i], curses.A_STANDOUT)
            else:
                stdscr.addstr(blurbheight + len(blurb) + i + 1, 3, options[i])
        
        # Show help
        if get_input:
            if input_type == "enum":
                stdscr.addstr(blurbheight + len(blurb) + len(options) + 2, 3, options_help[selected])
            elif input_type == "string":
                stdscr.addstr(blurbheight + len(blurb) + len(options) + 2, 3, ":_")

        # Get Input
        stdscr.addstr(0,0, "")
        stdscr.refresh()
        if get_input and input_type == "enum":
            res = stdscr.getch()
        elif get_input and input_type == "string":
            curses.echo()
            res = stdscr.getstr(blurbheight + len(blurb) + len(options) + 2, 5, 15)
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
            res = self.display(blurb, options, selected, True, options_help)
        elif res == curses.KEY_DOWN:
            # down arrow, increase selection
            if selected == len(options) - 1:
                selected = 0
            else:
                selected += 1
            res = self.display(blurb, options, selected, True, options_help)
        elif res == curses.KEY_ENTER or res == 10 or res == 13:
            res = selected
        else:
            res = self.display(blurb, options, selected, True, options_help)
        return res
        
    #################################################################################################################################################
    def menutree(self, initsel=0):
        os.system('mode con: cols=159 lines=34')
        global stdscr
        global debug
        blurb = ["This script will operate the RPi-R, testing a ", 
                "fluid and reporting the results. This program ", 
                "can also be used to update calibrations and ", 
                "geometries, or otherwise manage the rheometer.", 
                "", 
                "Current calibrations are:", 
                "",
                "\t(Dynamo)\tSpeed(Vd) = {:.3f} * Vd + {:.3f}".format(self.dynamo_cal[0], self.dynamo_cal[1]),
                "\t(30A HES)\tIms(Vhes) = {:.3f} * Vhes + {:.3f}".format(self.hes30A_cal[0], self.hes30A_cal[1]),
                "\t(5A HES)\tIms(Vhes) = {:.3f} * Vhes + {:.3f}".format(self.hes5A_cal[0], self.hes5A_cal[1])]
        
        options = [ "> Calibrate sensors",
                    "> Calibrate torque",
                    "> Quick test",
                    "> Custom test",
                    "> Quit"]
        
        help = [    "Calibrate dyamo and all 3 HES current sensors.",
                    "Stall torque measurement and calibration.",
                    "5 minute test of fluid at constant strain (~96.9s^-1).",
                    "Test fluid using custom settings.",
                    "Quit"]
        
        res = self.display(blurb, options, initsel, options_help=help)
        
        if res == 0:
            res = self.display([
                              "Sensor Calibration", 
                              "Step 1: Set up", 
                              " ",
                              "\t1. Allow motor to freely rotate.", 
                              "\t2. Attach ammeter in series with motor.",
                              "\t3. Ensure circuit is powered."], 
                              [
                              "\t> Continue",
                              "\t> Cancel"], get_input=True)
                          
            if res == 1: return 0
            ln = "./../logs/sensor_calibration_{}.csv".format(time.strftime("%d%m%y", time.gmtime()))
            
            if not debug: self.mot.start_poll(ln)
            self.set_relay(True)
            
            # variable inits
            cua      = dict()

            dr       = list()
            cr       = list()
            cra      = list()
            crb      = list()
            vms_hist = list()
            pv_hist  = list()

            # settings
            repetitions = 3 # default: 3
            readings = 1000   # default: 10

            for i in range(0, 17):

                if not debug: self.mot.set_pot(i*8)

                time.sleep(0.3)

                vms = 0.066 * (i * 8) + 2.422

                cua[(i * 8)] = 0.0
                dr.append(0.0)
                cr.append(0.0)
                cra.append(0.0)
                crb.append(0.0)

                for j in range(0, repetitions):
                    blurb = ["Sensor Calibration",
                             "Step 2: Read Ammeter",
                             " ",
                             "Supply voltage set to: {:.3f}V ({}/17)  ".format(vms, (i + 1)), 
                             " ", 
                             "Ammeter reading (A) ({}/{}): ".format((j + 1), repetitions)]
                    options = [""]
                    amr = self.display(blurb, options, input_type="string")
                    input_fine = True

                    try:
                        cua[(i * 8)] += float(amr)
                    except:
                        input_fine = False
                        blurb = ["Sensor Calibration",
                                 "Step 2: Read Ammeter",
                                 " ",
                                 "Supply voltage set to: {:.3f}V ({}/17)  ".format(vms, (i + 1)), 
                                 " ", 
                                 "Ammeter reading (A) ({}/{}): ".format((j + 1), repetitions),
                                 "Input needs to be a number!"]

                    while not input_fine:
                        amr = self.display(blurb, options, input_type="string")
                        input_fine = True
                        try:
                            cua[(i * 8)] += float(amr)
                        except:
                            input_fine = False
                            blurb = ["Sensor Calibration",
                                     "Step 2: Read Ammeter",
                                     " ",
                                     "Supply voltage set to: {:.3f}V ({}/17)  ".format(vms, (i + 1)), 
                                     " ", 
                                     "Ammeter reading (A) ({}/{}): ".format((j + 1), repetitions),
                                     "Input needs to be a number!"]
                    
                    # get sensor readings
                    
                    blurb = [" ", " Getting sensor data... "]
                    options = [" "]
                    self.display(blurb, options, get_input=False)
                    
                    for rep in range(0, readings):
                        dr[len(dr) - 1]   += self.mot.volts[0]
                        cr[len(cr) - 1]   += self.mot.volts[1]
                        cra[len(cra) - 1] += self.mot.volts[2]
                        crb[len(crb) - 1] += self.mot.volts[3]
                    
                        time.sleep(1.0 / readings)
                    
                    self.motor_cycle()

                vms_hist.append(vms)
                pv_hist.append(i * 8)

                dr[len(dr) - 1]     = dr[len(dr) - 1] / (repetitions * readings)
                cr[len(cr) - 1]     = cr[len(cr) - 1] / (repetitions * readings)
                cra[len(cra) - 1]   = cra[len(cra) - 1] / (repetitions * readings)
                crb[len(crb) - 1]   = crb[len(crb) - 1] / (repetitions * readings)

                cua[(i * 8)] = cua[(i * 8)] / repetitions
            
            if not debug: self.mot.clean_exit()
            self.set_relay(False)
            
            if debug: 
                tdyncal = self.dynamo_cal
                t30acal = self.hes30A_cal
                t5acal  = self.hes5A_cal
                ticovms = resx.cal_IcoVms
            else:

                cr      = np.array(cr, np.float64)
                cra     = np.array(cra, np.float64)
                crb     = np.array(crb, np.float64)

                tdyncal = self.cal_dynamo(dr, vms_hist)
                t30acal = self.cal_30ahes(cr, pv_hist, cua)
                t5acal  = self.cal_5ahes(cra, crb, pv_hist, cua)

                cu1     = t30acal[0] * cr + t30acal[1]
                cu2     = t5acal[0] * cra + t5acal[1]
                cu3     = t5acal[0] * crb + t5acal[1]

                ticovms = np.polyfit(vms_hist, (cu1 + cu2 + cu3) / 3, 1)
            
            blurb = ["Calibration results:", "",
                     "\t(Dynamo)\tSpeed(Vd) = {} * Vd + {}".format(tdyncal[0], tdyncal[1]),
                     "\t(30A HES)\tIms(Vhes) = {} * Vhes + {}".format(t30acal[0], t30acal[1]),
                     "\t(5A HES)\tIms(Vhes) = {} * Vhes + {}".format(t5acal[0], t5acal[1]), ""]
            options = ["\t> Save",
                       "\t> Discard"]
            help = ["  ", "  "]
            res = self.display(blurb, options, options_help=help)
            
            if res == 0:
                resx.cal_dynamo = tdyncal
                resx.cal_30AHES = t30acal
                resx.cal_5AHES = t5acal
                resx.cal_IcoVms = ticovms
                resx.writeout()
            elif res == 1:
                pass
            return 0
        elif res == 1:
            # recal stall torque

            # step 1: set up hardware (attach arm to cylinder, set up balance)
            blurb = [   "Motor Characteristic Calibration", 
                        "Step 1: Set up", 
                        " ",
                        "\t1. Attach arm to cylinder", 
                        "\t2. Set so arm hits balance",
                        "\t3. Ensure circuit is powered"
                    ]
            options = ["\t> Continue", 
                       "\t> Cancel"]
            help = ["", ""]
            res = self.display(blurb, options, options_help=help)
            if res == 1: return 1
            
            currents = [0] * 0
            supply_voltages = [0] * 0
            masses = [0] * 0
            
            self.set_relay(True)
            
            for i in range(0, 17):
                # step 2a: set voltage, read sensor information (Ims, Vms)
                # step 2b: read balance information (user input mass reading on balance)
                # step 2c: repeat steps a,b for multiple supply voltages (17, from PV=0 to PV=128, every 8)
                readings = 3
                self.mot.set_pot(i * 8)
                for j in range(0, readings):
                    # Get mass reading
                    blurb = [   "Motor Characteristic Calibration",
                                "Step 2: Reading Sensors",
                                " ",
                                "Supply voltage set to: {}V ({}/{})".format((8 * i) * 0.066 + 2.422, i, 17),
                                " ",
                                "Enter the balance reading, grams ({}/{}): ".format(j + 1, readings)]
                    options = [""]
                    help = [""]
                    res = self.display(blurb, options, options_help=help, input_type="string")
                    
                    # Get sensor data
                    for k in range(0, 100):
                        masses.append(float(res))
                        sensor_readings = [0, 0, 0, 0]
                        if not debug: sensor_readings = self.mot.read_sensors()
                        current = ((resx.cal_30AHES[0] * sensor_readings[1] + resx.cal_30AHES[1]) + 
                                (resx.cal_5AHES[0] * sensor_readings[2] + resx.cal_5AHES[1]) + 
                                (resx.cal_5AHES[0] * sensor_readings[3] + resx.cal_5AHES[1])) / 3
                        supply_voltage = (8 * i) * 0.066 + 2.422
                        currents.append(current)
                        supply_voltages.append(supply_voltage)
                        time.sleep(0.01)
                    
                    # Cycle motor
                    self.motor_cycle()
                    self.set_relay(False)
                    time.sleep(3)
                    self.set_relay(True)
                    
            self.motor.clean_exit()
            self.set_relay(False)
            
            Larm = 0.0656   # length of arm attached to motor, in m
            g    = 9.81     # acceleration due to gravity, m/(s^2)
            
            stall_torques = np.array(masses, np.float64) * g * Larm
            TsFit         = np.polyfit(supply_voltages, stall_torques, 1)
            IemFit        = np.polyfit(supply_voltages, currents - (np.array(supply_voltages) * resx.cal_IcoVms[0] + resx.cal_IcoVms[1]), 1)
            
            blurb = ["Calibration results:", 
                     " ",
                     "\t(Stall Torque)\tTs(Vms) = {} * Vms + {}".format(TsFit[0], TsFit[1]),
                     "\t(EMF Current)\tIem(Vms) = {} * Vms + {}".format(IemFit[0], IemFit[1])]
            options = ["\t> Save",
                       "\t> Discard"]
            help = ["  ", "  "]
            res = self.display(blurb, options, options_help=help)
            
            if res == 0:
                resx.cal_TsVms = TsFit
                resx.cal_IemfVms = IemFit
                resx.writeout()
            elif res == 1:
                pass
            return 1
        elif res == 2:
            # test a sample (default settings - PV=48, for 5 minutes)
            blurb = ["Rheometry Test (Quick)", 
                     "Settings:",
                     "\tRun length: \t5 minutes",
                     "\tStrain rate:\t96.9 (1/s)", 
                     " "]
            options = ["> Continue", 
                       "> Cancel"]
            help = [" ", " "]
            res = self.display(blurb, options, options_help=help)

            if res == 0:
                # run test
                ln = self.run_test()
                
                # calculate viscosity
                visco_res = self.calc_visc(ln, 15)
                average_viscosity = np.average(visco_res)

                # display result
                blurb = ["Finished!"," ","Results saved in {}".format(ln), "Average Viscosity: {:.3f} Pa.s".format(average_viscosity)]
                options = ["> Continue"]
                
                res = self.display(blurb, options)
            else:
                # cancel
                pass
            return 2
        elif res == 3:
            # test a sample (custom settings - load from xml or edit default)
            return 3
        elif res == 4:
            # quit
            return 4

    #################################################################################################################################################
    def simple_mode(self):
        os.system('mode con: cols=159 lines=34')
        global stdscr
        global debug
        
        blurb =     [
                    "Welcome to RPi-R: Simple rheometry recording with a Raspberry Pi",
                    ]
        options =   [
                    "> Run sample (quick)",
                    "> Run sample (custom)",
                    "> View results",
                    "> Re-calibrate sensors",
                    "> View Readme",
                    "> Quit"
                    ]
        res = self.display(blurb, options)
        
        if res == 0 or res == 1:
            # Run sample
            
            length = 300  # run length, in seconds
            gd_expr = "48"  # strain rate, in inverse seconds
            
            if res == 1:
                # Get custom settings
                
                # Run length
                inp_k = False
                extra_info = " "
                
                while not inp_k:
                    blurb = ["Run sample - setup",
                             "",
                             "Length:     --",
                             "Function:   --",
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
                             "Length:     {}s".format(length),
                             "Function:   --",
                             "",
                             extra_info,
                             "Enter strain rate function (inverse seconds)",
                             "",
                             "Input in form of an expression (gamma dot = ...)"]
                    options = [""]
                    
                    gd_expr = self.display(blurb, options, get_input=True, input_type="string")
                    
                    inp_k = True
                    
                    try:
                        t = sp.Symbol('t')
                        gd = sp.Symbol('gd')
                        expr = pe(gd_expr) - gd
                        val = sp.solve(expr, gd)
                        if len(val) > 1: raise Exception("you dun entered it rong lol")
                    except:
                        inp_k = False
                        extra_info = "Input not recognised (ensure it is a function of 't', or a constant)"
            
            blurb = ["Run sample - setup",
                     "",
                     "Length:    {}s".format(length),
                     "Function:  gd = {}".format(gd_expr),
                     ""]
            options = ["> Continue", "> Quit"]
            res = self.display(blurb, options)
            
            if res == 1: return 1
            
            ln = self.run_test(length, gd_expr)
            
            blurb = ["Run sample - complete", "", "output log saved as {}".format(ln)]
            options = ["> Continue"]
            res = self.display(blurb, options)
        
        elif res == 2:
            # View results
            blurb = ["View Results - Latest"]
            recent_logs = sorted(glob("./../logs/rheometry_test_*.csv"))
            
            ## Display most recent log results
            # "| log name ... | average viscosity result ... |"
            blurb.append("Log:      {}".format(recent_logs[-1]))
            
            norm_visc = simple_get_results(recent_logs[-1])
            
            av_norm_visc = np.average(norm_visc)
            
            #blurb.append("Av. Visc: {}".format(av_norm_visc))
            
            blurb.append(" ")
            
            blurb.append(" More files in logs folder")
            
            blurb.append(" ")
            
            options = ["> Continue", "> Plot"]
            
            res = self.display(blurb, options)
            
            ## List older files...
            # "> June 12"
            # "> June 10"
            pass
        elif res == 3:
            # Recalibrate
            pass
        elif res == 4:
            # View readme/manual
            blurb = ["RPi-R: Simple rheometry indicator",
                     " ",
                     "Power into the motor to maintain a set strain rate",
                     "is related to the viscosity of the fluid in the cell.",
                     "",
                     "An unknown fluid can be characterised by comparing",
                     "the power draw of the loadless cell to the draw of the",
                     "loaded cell."]
            options = ["> Continue"]
            
            self.display(blurb, options)
        else:
            return 4
        return 1
            
    #################################################################################################################################################
    def run_test(self, length=300, gd_expr="48"):
        self.display(["Rheometry Test", "", ""],[""], get_input=False)
        ln = "./../logs/rheometry_test_{}.csv".format(time.strftime("%d%m%y_%H%M", time.gmtime()))
        
        if not debug: self.mot.start_poll(ln)
        
        gd = sp.Symbol('gd')
        
        for i in range(0, length):
            t = copy.copy(i)
            
            expr = pe(gd_expr) - gd
            
            gd_val = eval(str(sp.solve(expr, gd)[0]))
            
            self.mot.set_pot(gd_val)
            
            vms = 0.066 * self.mot.pot.lav + 2.422
            width = 40
            perc = int(math.ceil((i / float(length)) * width))
            neg_perc = int(math.floor(((float(length) - i) / length) * width))
            blurb = [
                    "Rheometry Test", 
                    "Supply voltage set to: {:.3f}V\tTime remaining: {}s   ".format(vms, (length - i)),
                    "[{}{}]".format("#" * perc, " " * neg_perc)
                    ]
            options = [" "]
            self.display(blurb, options, get_input=False)
            time.sleep(1)
        
        self.mot.clean_exit()
        return ln
        
    #################################################################################################################################################
    def calc_visc(self, filename, fill_vol):
        self.fill_height = fill_vol / self.dxsa
        datf = pd.read_csv(filename)

        # Split up csv columns
        t   = np.array(datf['t'], np.float64)
        st  = t - t[0]
        dr  = np.array(datf['dr'], np.float64)
        cr  = np.array(datf['cr'], np.float64)
        pv  = np.array(datf['pv'], np.float64)
        cra = np.array(datf['cr2a'], np.float64)
        crb = np.array(datf['cr2b'], np.float64)
        
        # Filtering: aye or naw?
        if True:
            dr = np.array(filter(st, dr, method="butter",A=2, B=0.001))
            cr = np.array(filter(st, cr, method="butter",A=2, B=0.001))
            cra = np.array(filter(st, cra, method="butter",A=2, B=0.001))
            crb = np.array(filter(st, crb, method="butter",A=2, B=0.001))
        
        # Calculate viscosity etc
        Ims     = resx.cal_30AHES[0] * cr + resx.cal_30AHES[1]
        Ims    += resx.cal_5AHES[0] * cra + resx.cal_5AHES[1]
        Ims    += resx.cal_5AHES[0] * crb + resx.cal_5AHES[1]
        Ims     = Ims / 3
        sp_rpms = resx.cal_dynamo[0] * dr + resx.cal_dynamo[1]
        sp_rads = (sp_rpms * 2 * np.pi) / 60
        sn_rpms = 5.13 * pv + 15.275
        Vms      = 0.066 * pv + 2.422

        Icoil   = resx.cal_IcoVms[0] * Vms + resx.cal_IcoVms[1]
        Iemf    = resx.cal_IemfVms[0] * Vms + resx.cal_IemfVms[1]
        Ts      = resx.cal_TsVms[0] * Vms + resx.cal_TsVms[1]

        T       = (Ims - Icoil) / (Iemf / Ts)
        
        tau     = T / (2 * np.pi * self.ri * self.ri * self.fill_height) 
        gam_dot = (sp_rads * self.ri) / (self.ro - self.ri)
        
        mu      = tau / gam_dot
        
        return mu
       
    #################################################################################################################################################     
    def set_strain_rate(self, value):
        desired_speed = value * (self.ro - self.ri) / self.ri  # in rads
        desired_speed = desired_speed * 60 / (2 * np.pi)  # in rpms
        if self.mot.control_stopped:
            set_pv = int((desired_speed - self.spf[1]) / self.spf[0])
            self.mot.set_pot(set_pv)
        else:
            self.mot.update_setpoint(desired_speed)

    #################################################################################################################################################
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
    
    #################################################################################################################################################
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
    
    #################################################################################################################################################
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
            vdict[str(vmsm[i])] = av_spd[i]

        spd_long = np.array(range(0, len(vmsm)), np.float64)
        for i in range(0, len(vms)):
            spd_long[i] = vdict[str(vms[i])]
 
        coeffs = np.polyfit(dr, spd_long, 1)
        return coeffs
        
    #################################################################################################################################################
    def motor_cycle(self, show_screen=True):
        
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
            
    #################################################################################################################################################
    def set_relay(self, value):
        self.motor_running = value
        if value:
            self.mot.actuate()
        else:
            self.mot.deactuate()
        
if __name__ == "__main__" and True:
    # setup curses window
    #rows, columns = os.popen('stty size', 'r').read().split()
    bigscr = curses.initscr()
    stdscr = curses.newwin(34, 75, 1, 1)
    stdscr.border(0)
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
    
    if True:
        #a = r.menutree()
        a = r.simple_mode()
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
    else:
        try:
            res = 0
            while res != 4:
                res = r.menutree(initsel=res)
        except:
            pass
        else:
            pass
        finally:
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()
elif __name__ == "__main__" and False:
    datf = pd.read_csv("./../logs/sensor_calibration_100417.csv")
    r = rheometer()
    cr = np.array(datf['cr'], np.float64)
    cra = np.array(datf['cr2a'], np.float64)
    crb = np.array(datf['cr2b'], np.float64)

    vms = np.array(datf['pv'], np.float64)

    cua = {0   : 0.51, 
           8   : 0.53, 
           16  : 0.54, 
           24  : 0.56, 
           32  : 0.57, 
           40  : 0.59, 
           48  : 0.61, 
           56  : 0.62, 
           64  : 0.64, 
           72  : 0.65, 
           80  : 0.67, 
           88  : 0.68, 
           96  : 0.7, 
           104 : 0.71, 
           112 : 0.73, 
           120 : 0.74, 
           128 : 0.76}

    cal5 = r.cal_5ahes(cra, crb, vms, cua)
    print cal5
