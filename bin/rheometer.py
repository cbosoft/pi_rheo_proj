#
# rheometer.py
#
# class object controlling the rheometer from the rasbperry pi
#


packages_missing = [""]
print "Loading packages.."

print "\tplot_help.py"
from plothelp import fit_line
from plothelp import read_logf
from plothelp import simple_get_results

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
    from math import sin
    from math import cos
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
    print "\tpyaudio"
    import pyaudio as pa
except ImportError as ex:
    packages_missing.append("pippyaudio")
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
    #print "Automatically trying to obtain missing packages...\n"
    #for i in range(1, len(packages_missing)):
    #    if packages_missing[i][:3] == "apt":
    #        os.system("sudo apt-get install {}".format(packages_missing[i][3:]))
    #    elif packages_missing[i][:3] == "pip":
    #        os.system("sudo -H pip install {}".format(packages_missing[i][3:]))

    crit_fail = False
    for p in packages_missing:
        if p[:3] == "crt":
            crit_fail = True

    if crit_fail:
        print "Some packages suggest something worse is going on:\n"
        for p in packages_missing:
            print "\t{}".format(p[3:])
        print "\nIs there a typo in the rheometer script? Broken python install?"
    print "Press enter to continue"
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
        #print "Initialising motor..."
        self.mot = motor(**motor_params)
    
    def display(self, blurb, options, selected=0, get_input=True, options_help="NONE", input_type="enum"):
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
            
        stdscr.addstr(3, 3,  r"                                 _        _                                     ")
        stdscr.addstr(4, 3,  r"                      _ __ _ __ (_)  _ __| |__   ___  ___                       ")
        stdscr.addstr(5, 3,  r"                     | '__| '_ \| | | '__| '_ \ / _ \/ _ \                      ")
        stdscr.addstr(6, 3,  r"                     | |  | |_) | |_| |  | | | |  __/ (_) |                     ")
        stdscr.addstr(7, 3,  r"                     |_|  | .__/|_(_)_|  |_| |_|\___|\___/                      ")
        stdscr.addstr(8, 3,  r"                          |_|  Raspberry Pi Rheometer v{}                    ".format(version))
        stdscr.addstr(9, 3,  r"{}{}".format(mode_string.center(40), motor_string.center(40)))
        stdscr.addstr(10, 3, r"_____________________________________________________________________")

        blurbheight = 12

        # Display Blurb
        for i in range(0, len(blurb)):
            stdscr.addstr(blurbheight + i, 3, blurb[i])
        
        # Show Options
        for i in range(0, len(options)):
            if selected == i:
                stdscr.addstr(blurbheight + len(blurb) + i + 1, 3, options[i].center(80), curses.A_STANDOUT)
            else:
                stdscr.addstr(blurbheight + len(blurb) + i + 1, 3, options[i].center(80))
        
        # Show help
        if get_input:
            if input_type == "enum":
                stdscr.addstr(blurbheight + len(blurb) + len(options) + 2, 3, options_help[selected].center(80))
            elif input_type == "string":
                stdscr.addstr(blurbheight + len(blurb) + len(options) + 2, 3, ":_")

        # Get Input
        stdscr.addstr(0,0, "")
        stdscr.refresh()
        if get_input and input_type == "enum":
            res = stdscr.getch()
        elif get_input and input_type == "string":
            curses.echo()
            # TODO: Draw box around input, so that you know how long it can be
            # o----------------------------------------o
            # |                                        |
            # o----------------------------------------o
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
    def simple_mode(self, initsel=0):
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
        res = self.display(blurb, options, selected=initsel)
        
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
                             "Log tag:    --",
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
                             "Log tag:    --",
                             "",
                             extra_info,
                             "Enter strain rate function (inverse seconds)",
                             "",
                             "Input in form of an expression (gamma dot = ...)",
                             "NOTE:",
                             "\tMinimum value =   5 (s^-1)",
                             "\tMaximum value = 250 (s^-1)"]
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
                         "Length:     {}s".format(length),
                         "Function:   gd = {} (s^-1)".format(gd_expr),
                         "Log tag:    --",
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
                     "Length:    {}s".format(length),
                     "Function:  gd = {} (s^-1)".format(gd_expr),
                     "Log tag:    \"{}\"".format(tag),
                     ""]
            options = ["> Continue", "> Quit"]
            res = self.display(blurb, options)
            
            if res == 1: return 1
            
            ln = self.run_test(tag, length, gd_expr)
            
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
                    "Supply voltage set to:_ _ _ _ _ _ _ _ {:.3f} V".format(vms),
                    "Target strain rate: _ _ _ _ _ _ _ _ _ {:.3f} (s^-1)".format(gd_val),
                    "Value sent to potentiometer:_ _ _ _ _ {}".format(self.mot.pot.lav),
                    "Time remaining: _ _ _ _ _ _ _ _ _ _ _ {}s   ".format(length - i),
                    "[{}{}]".format("#" * perc, " " * neg_perc)
                    ]
            options = [" "]
            self.display(blurb, options, get_input=False)
            time.sleep(1)
        
        #recrdr.stop_recording()
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
            set_pv = int((desired_speed - resx.cal_Vnl[1]) / resx.cal_Vnl[0])
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
        
if __name__ == "__main__":
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
    
    menu_mode_simple = True
    catch_mode_on = True
    
    if "-c" in sys.argv: menu_mode_simple = False # complex calculation mode
    if "-r" in sys.argv: catch_mode_on = False # raw operation, errors are not caught.
    

    if not catch_mode_on:
        if menu_mode_simple:
            a = r.simple_mode()
        else:
            a = r.complex_mode()
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
    else:
        try:
            res = 0
            while res != 4:
                if menu_mode_simple:
                    res = r.simple_mode(initsel=res)
                else:
                    res = r.complex_mode(initsel=res)
        except:
            pass
        else:
            pass
        finally:
            curses.nocbreak()
            stdscr.keypad(0)
            curses.echo()
            curses.endwin()
