#
# rheometer.py
#
# class object controlling the rheometer from the rasbperry pi
#

import time
import numpy as np
import pandas as pd
import resx
import sys
import curses
import math
import os

from motor import motor
from filter import filter
from plothelp import fit_line

try:
    import spidev
except:
    debug = True
else:
    debug = False
    

class rheometer(object):
    # misc
    version = "0.1.0 pre alpha"
    
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
    
    def __init__(self, motor_params={'log_dir':'./logs'}):
        print motor_params
        self.mot = motor(**motor_params)
            
    def get_rheometry(self, strain_rate, run_length):
        pass
    
    def display(self, blurb, options, selected=0, get_input=True, options_help="NONE", plot_title="Plot", plot_x_title="x", plot_y_title="y", plot_x=[1, 2, 3, 4, 5], plot_y=[2, 2, 2, 2, 2], input_type="enum"):
        global stdscr
        global plotwin
        global debug
        stdscr.clear()
        stdscr.border(0)
        plotwin.clear()
        plotwin.border(0)
        if options_help == "NONE": options_help = [""] * len(options)

        # TEST DATA #
        plot_x = np.linspace(1, 5)
        plot_y = (np.exp(-plot_x))

        # Plot
        # width = 50, height = 25
        plotwin.addstr(2, 1, "{}{}{}".format(" " * ((48 - len(plot_title)) / 2), plot_title, " " * ((48 - len(plot_title)) / 2)))
        
        # draw axis
        for i in range(4, 23):
            plotwin.addstr(i, 4, "|")
        for i in range(5, 45):
            plotwin.addstr(22, i, "-")
        plotwin.addstr(22, 4, "o")

        # draw titles
        plotwin.addstr(23, 1, "{}{}{}".format(" " * ((48 - len(plot_x_title)) / 2), plot_x_title, " " * ((48 - len(plot_x_title)) / 2)))
        y_title_centred = "{}{}{}".format(" " * ((24 - len(plot_y_title)) / 2), plot_y_title, " " * ((24 - len(plot_y_title)) / 2))
        for i in range(0, len(y_title_centred)):
            plotwin.addstr(i + 1, 2, y_title_centred[i])

        # get scale
        deltax = max(plot_x)
        deltay = max(plot_y)
        plot_x = np.array(plot_x)
        plot_x = plot_x * (29 / deltax)
        plot_y = np.array(plot_y)
        plot_y = plot_y * (17 / deltay)

        # plot data
        for i in range(0, len(plot_x)):
            plotwin.addstr(21 - int(plot_y[i]), 4 + int(plot_x[i]), "X")

        # RPi-R header
        stdscr.addstr(3, 3, r"____________ _       ______ ")
        stdscr.addstr(4, 3, r"| ___ \ ___ (_)      | ___ \ ")
        stdscr.addstr(5, 3, r"| |_/ / |_/ /_ ______| |_/ /")
        stdscr.addstr(6, 3, r"|    /|  __/| |______|    / ")
        stdscr.addstr(7, 3, r"| |\ \| |   | |      | |\ \ ")
        stdscr.addstr(8, 3, r"\_| \_\_|   |_|      \_| \_|")
        stdscr.addstr(10, 3, r"Raspberry Pi Rheometer {}".format(self.version))

        blurbheight = 12        
        
        if debug: 
            stdscr.addstr(blurbheight, 3, r" !! -->> DEBUG MODE <<-- !!")
            blurbheight += 2

        # Display Blurb
        for i in range(0, len(blurb)):
            stdscr.addstr(blurbheight + i, 3, blurb[i])
        
        # Show Options
        for i in range(0, len(options)):
            if selected == i:
                stdscr.addstr(blurbheight + len(blurb) + i, 3, options[i], curses.A_STANDOUT)
            else:
                stdscr.addstr(blurbheight + len(blurb) + i, 3, options[i])
            
        # Show help
        if get_input:
            if input_type == "enum":
                stdscr.addstr(blurbheight + len(blurb) + len(options) + 2, 3, options_help[selected])
            elif input_type == "string":
                stdscr.addstr(blurbheight + len(blurb) + len(options) + 2, 3, ":_")

        # Get Input
        stdscr.addstr(0,0, "")
        stdscr.refresh()
        plotwin.refresh()
        if get_input and input_type == "enum":
            res = stdscr.getch()
        elif get_input and input_type == "string":
            curses.echo()
            res = stdscr.getstr(blurbheight + len(blurb) + len(options) + 2, 5, 5)
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
                "\t(Dynamo)\tSpeed(Vd) = {} * Vd + {}".format(self.dynamo_cal[0], self.dynamo_cal[1]),
                "\t(30A HES)\tIms(Vhes) = {} * Vhes + {}".format(self.hes30A_cal[0], self.hes30A_cal[1]),
                "\t(5A HES)\tIms(Vhes) = {} * Vhes + {}".format(self.hes5A_cal[0], self.hes5A_cal[1])]
        
        options = [ "> Recalibrate sensors",
                    "> Recalibrate torque",
                    "> Quick test",
                    "> Custom test",
                    "> Quit"]
        
        help = [    "Simple sweep of voltages used to recalibrate sensors.",
                    "!! - Yet to be implemented.",
                    "5 minute test of fluid at constant strain (~96.9s^-1).",
                    "Test fluid using custom settings.",
                    ""]
        
        res = self.display(blurb, options, initsel, options_help=help)
        
        if res == 0:
            blurb = ["Sensor recalibration.", "", "Run length:"]
            options = ["> Long (~10 minutes)", "> Medium (~5 minutes)", "> Short (~2 minutes)"]
            help = ["  ", "  ", "  "]
            res = self.display(blurb, options, options_help=help)

            if res == 0:
                step = 5
            elif res == 1:
                step = 2.5
            elif res == 2:
                step = 0.25
                
            self.display(["Running calibration (standard sweep, 2.422V to 10.87V)."],[""], get_input=False)
            ln = "./../logs/sensor_calibration_{}.csv".format(time.strftime("%d%m%y", time.gmtime()))
            
            if not debug: self.mot.start_poll(ln)
            
            for i in range(0, 129):
                self.mot.set_pot(i)
                vms = 0.066 * i + 2.422
                stdscr.addstr(16, 3, "Supply voltage set to: {:.3f}V\tTime remaining: {}s   ".format(vms, (128 - i) * step))
                width = 40
                perc = int(math.ceil((i * float(step) / 128.0) * width))
                neg_perc = int(math.floor(((128.0 - i) * step / 128.0) * width))
                stdscr.addstr(17, 3, "[{}{}]".format("#" * perc, " " * neg_perc))
                stdscr.refresh()
                time.sleep(step)
            
            self.mot.clean_exit()
            
            if debug: 
                tdyncal = self.dynamo_cal
                t30acal = self.hes30A_cal
                t5acal = self.hes5A_cal
            else:
                # data contained in log file $ln can be used to calibrate dynamo and HES sensor data"
                datf    = pd.read_csv(ln)
                st      = np.array(datf['t'], np.float64)
                st      = st - st[0]
                cr      = np.array(datf['cr'], np.float64)
                dr      = np.array(datf['dr'], np.float64)
                cra     = np.array(datf['cr2a'], np.float64)
                crb     = np.array(datf['cr2b'], np.float64)

                tdyncal = self.cal_dynamo(st, dr, pv)
                t30acal = self.cal_30ahes(st, cr, pv)
                t5acal = self.cal_5ahes(st, cra, crb, pv)
            
            blurb = ["Calibration results:", "",
                     "\t(Dynamo)\tSpeed(Vd) = {} * Vd + {}".format(tdyncal[0], tdyncal[1]),
                     "\t(30A HES)\tIms(Vhes) = {} * Vhes + {}".format(t30acal[0], t30acal[1]),
                     "\t(5A HES)\tIms(Vhes) = {} * Vhes + {}".format(t5acal[0], t5acal[1]), ""]
            options = ["\t(1) Save",
                       "\t(2) Discard"]
            help = ["  ", "  "]
            res = self.display(blurb, options, options_help=help)
            
            if res == 0:
                resx.cal_dynamo = tdyncal
                resx.cal_30AHES = t30acal
                resx.cal_5AHES = t5acal
                resx.writeout()
            elif res == 1:
                pass
            return 0
        elif res == 1:
            # recal stall torque

            # step 1: set up hardware (attach arm to cylinder, set up balance)
            blurb = [   "Motor Characteristic Calibration", 
                        "", 
                        "Step 1: Set up.", 
                        "This script will operate the RPi-R, testing a ",
                        "The arm must be attached to the inner cylinder ", 
                        "and positioned such that when the motor rotates,",
                        "the arm hits the balance",
                        "Continue when ready."]
            options = ["> Continue", "> Cancel"]
            help = ["", ""]
            res = self.display(blurb, options, options_help=help)
            if res == 1: return 1

            for i in range(0, 17):
                # step 2a: set voltage, read sensor information (Ims, Vms)
                # step 2b: read balance information (user input mass reading on balance)
                # step 2c: repeat steps a,b for multiple supply voltages (17, from PV=0 to PV=128, every 8)

                self.mot.set_pot(i * 8)
                for j in range(0, 10):
                    sensor_readings = [0, 0, 0, 0]
                    if not debug: sensor_readings = self.mot.read_sensors()
                    blurb = [   "Motor Characteristic Calibration",
                                "",
                                "Step 2: Reading Sensors",
                                "",
                                "Supply voltage set to: {}".format((8 * i) * 0.066 + 2.422),
                                "Sensor\t\tReading\t\tValue",
                                "30AHES\t\t{:.3f}\t\t{:.3f}".format(sensor_readings[1], resx.cal_30AHES[0] * sensor_readings[1] + resx.cal_30AHES[1]),
                                "5AHES1\t\t{:.3f}\t\t{:.3f}".format(sensor_readings[2], resx.cal_5AHES[0] * sensor_readings[2] + resx.cal_5AHES[1]),
                                "5AHES2\t\t{:.3f}\t\t{:.3f}".format(sensor_readings[3], resx.cal_5AHES[0] * sensor_readings[3] + resx.cal_5AHES[1]),
                                "",
                                "Enter the balance reading, grams ({}/10):".format(j)]
                    options = [""]
                    help = [""]
                    res = self.display(blurb, options, options_help=help, input_type="string")
                    
                    # plot results?
                    # save information
                    # update resx calibrations

            return 1
        elif res == 2:
            # test a sample (default settings - PV=48, for 5 minutes)
            blurb = ["Rheometry quick run:", "\tRun length: \t5 minutes","\tStrain rate:\t96.9 (1/s)", ""]
            options = ["> Continue", "> Cancel"]
            help = [" ", " "]
            res = self.display(blurb, options, options_help=help)

            if res == 0:
                # run test
                self.display(["Running calibration (standard sweep, 2.422V to 10.87V)."],[""], get_input=False)
                ln = "./../logs/rheometry_test_{}.csv".format(time.strftime("%H%M_%d%m%y", time.gmtime()))
                
                if not debug: self.mot.start_poll(ln)
                
                self.mot.set_pot(48)
                vms = 0.066 * 48 + 2.422

                for i in range(0, 300):
                    stdscr.addstr(16, 3, "Supply voltage set to: {:.3f}V\tTime remaining: {}s   ".format(vms, (300 - i)))
                    width = 40
                    perc = int(math.ceil((i / 300.0) * width))
                    neg_perc = int(math.floor(((300.0 - i) / 300.0) * width))
                    stdscr.addstr(17, 3, "[{}{}]".format("#" * perc, " " * neg_perc))
                    stdscr.refresh()
                    time.sleep(1)
                
                self.mot.clean_exit()
                visco_res = calc_visc(self, ln, 15)
                blurb = ["Average Viscosity: {:.3f} Pa.s".format(visco_res)]
                options = ["> Save results plot", "> Continue"]
                options_help = ["Save resulting rheometry plot to file", "Discard results, return to menu"]
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
    
    def get_viscosity(self, strain_rate, run_length):
        variable_strain = True
        
        self.mot.start_poll()
        
        try:
            iterator = iter(strain_rate)
        except TypeError:
            variable_strain = False
        print "Reading data ({} s)...".format(run_length)
        try:
            if variable_strain:
                for i in range(0, len(strain_rate)):
                    self.set_strain_rate(strain_rate[i])
                    time.sleep(run_length / len(strain_rate))
            else:
                self.set_strain_rate(strain_rate)
                time.sleep(run_length)

            self.mot.clean_exit()
            print "Calculating viscosity..."
            return self.calc_visc(self.mot.this_log_name)

        except KeyboardInterrupt:
            self.mot.clean_exit()
            return 0  # Operation was cancelled

    def calc_visc(self, filename, fill_vol):
        self.fill_height = fill_vol / self.dxsa
        datf = pd.read_csv(filename)

        # Split up csv columns
        t = datf['t']
        st = t - t[0]
        dr = datf['dr']
        cr = datf['cr']
        pv = datf['pv']
        
        # Fix out of range current readings
        for i in range(1, len(cr)):
            if cr[i] < 2.28: cr[i] = 2.28
            if cr[i] > 2.4: cr[i] = 2.4
        
        # Filtering: aye or naw?
        if True:
            dr = np.array(filter(st, dr, method="butter",A=2, B=0.001))
            cr = np.array(filter(st, cr, method="butter",A=2, B=0.001))
        
        # Calculate viscosity etc
        cu      = (-956.06 * (cr ** 3)) + (6543.97 * (cr ** 2)) + (-14924.369 * cr) + 11341.612
        sp_rpms = dr * 316.451 - 163.091
        sp_rads = (sp_rpms * 2 * np.pi) / 60
        sn_rpms = 5.13 * pv + 15.275
        vo      = 0.0636 * pv + 2.423
        pe      = cu * vo
        T       = 0.000001054 * pe - 0.000001488
        tau     = T / (2 * np.pi * self.ri * self.ri * self.fill_height) 
        gam_dot = (sp_rads * self.ri) / (self.ro - self.ri)
        
        #holy moses, more filtering?
        if False:
            tau     = filter(st, tau, method="butter", A=2, B=0.001)
            gam_dot = filter(st, gam_dot, method="butter", A=4, B=0.001)
        
        __, __, coeffs = fit_line(gam_dot, tau, 1)
        
        return coeffs[0]
            
    def set_strain_rate(self, value):
        desired_speed = value * (self.ro - self.ri) / self.ri  # in rads
        desired_speed = desired_speed * 60 / (2 * np.pi)  # in rpms
        if self.mot.control_stopped:
            set_pv = int((desired_speed - self.spf[1]) / self.spf[0])
            self.mot.set_pot(set_pv)
        else:
            self.mot.update_setpoint(desired_speed)

    def cal_30ahes(self, st, cr, pv):
        crf = filter.filter(st, cr, method="butter", A=2, B=0.001)
        crf = filter.filter(st, crf, method="gaussian", A=100, B=100)

        cu = [0] * 0
        pv_s = [0] * 0

        for p in pv:
            if p == 0:
                cu.append(0.48)
                pv_s.append(0)
            elif p == 8:
                cu.append(0.51)
                pv_s.append(8)
            elif p == 16:
                cu.append(0.53)
                pv_s.append(16)
            elif p == 24:
                cu.append(0.55)
                pv_s.append(24)
            elif p == 32:
                cu.append(0.57)
                pv_s.append(32)
            elif p == 40:
                cu.append(0.59)
                pv_s.append(40)
            elif p == 48:
                cu.append(0.6)
                pv_s.append(48)
            elif p == 56:
                cu.append(0.62)
                pv_s.append(56)
            elif p == 64:
                cu.append(0.63)
                pv_s.append(64)
            elif p == 72:
                cu.append(0.65)
                pv_s.append(72)
            elif p == 80:
                cu.append(0.67)
                pv_s.append(80)
            elif p == 88:
                cu.append(0.69)
                pv_s.append(88)
            elif p == 96:
                cu.append(0.7)
                pv_s.append(96)
            elif p == 104:
                cu.append(0.73)
                pv_s.append(104)
            elif p == 112:
                cu.append(0.73)
                pv_s.append(112)
            elif p == 120:
                cu.append(0.75)
                pv_s.append(120)
            elif p == 128:
                cu.append(0.82)
                pv_s.append(128)

        # CU AS A FUNC OF PV
        coeffs = np.polyfit(pv_s, cu, 1)  # fit linear equation to data read manually
        pvlo = np.arange(0, 128, (128.0 / len(pv)))
        pvlo = [math.floor(p) for p in pvlo]
        pvlo = np.array(pvlo)
        cul = coeffs[0] * pvlo + coeffs[1]

        # Remove unwanted outlying data
        min_l = 10000
        max_l = -1
        skip = 10000
        cr = cr[min_l:max_l:skip]
        crf = crf[min_l:max_l:skip]
        cul = cul[min_l:max_l:skip]

        crstd = np.std(cr)
        crfstd = np.std(crf)

        # Set up figure
        f = plt.figure(figsize=(8, 8))
        ax = f.add_subplot(111)

        # Plot data and trendline: CRF vs CU
        __, __, coeffs = fit_line(crf, cul, 1)
        return coeffs
    
    def cal_5ahes(self, st, cra, crb, pv):
        cra     = filter.filter(st, cra, method="butter", A=2, B=0.001)
        crb     = filter.filter(st, crb, method="gaussian", A=100, B=100)
        pv      = np.array(datf['pv'])
        crf     = 0.5 * (cra + crb)
        cu = [0] * 0
        pv_s = [0] * 0

        # From manual ammeter read
        for p in pv:
            if p == 0:
                cu.append(0.48)
                pv_s.append(0)
            elif p == 8:
                cu.append(0.51)
                pv_s.append(8)
            elif p == 16:
                cu.append(0.53)
                pv_s.append(16)
            elif p == 24:
                cu.append(0.55)
                pv_s.append(24)
            elif p == 32:
                cu.append(0.57)
                pv_s.append(32)
            elif p == 40:
                cu.append(0.59)
                pv_s.append(40)
            elif p == 48:
                cu.append(0.6)
                pv_s.append(48)
            elif p == 56:
                cu.append(0.62)
                pv_s.append(56)
            elif p == 64:
                cu.append(0.63)
                pv_s.append(64)
            elif p == 72:
                cu.append(0.65)
                pv_s.append(72)
            elif p == 80:
                cu.append(0.67)
                pv_s.append(80)
            elif p == 88:
                cu.append(0.69)
                pv_s.append(88)
            elif p == 96:
                cu.append(0.7)
                pv_s.append(96)
            elif p == 104:
                cu.append(0.73)
                pv_s.append(104)
            elif p == 112:
                cu.append(0.73)
                pv_s.append(112)
            elif p == 120:
                cu.append(0.75)
                pv_s.append(120)
            elif p == 128:
                cu.append(0.82)
                pv_s.append(128)

        # CU AS A FUNC OF PV
        coeffs = np.polyfit(pv_s, cu, 1)  # fit linear equation to data read manually
        pvlo = np.arange(0, 128, (128.0 / len(pv)))
        pvlo = [math.floor(p) for p in pvlo]
        pvlo = np.array(pvlo)
        cul = coeffs[0] * pvlo + coeffs[1]

        # Remove unwanted outlying data
        min_l = 10000
        max_l = -1
        skip = 10000
        cr = cr[min_l:max_l:skip]
        crf = crf[min_l:max_l:skip]
        cul = cul[min_l:max_l:skip]

        crstd = np.std(cr)
        crfstd = np.std(crf)

        # Set up figure
        f = plt.figure(figsize=(8, 8))
        ax = f.add_subplot(111)

        # Plot data and trendline: CRF vs CU
        __, __, coeffs = fit_line(crf, cul, 1)
    
    def cal_dynamo(self, st, rv, pv):
        # Read csv
        datf = open("./../logs/voltvval.csv", "r")
        datl = datf.readlines()
        datf.close()

        # Create lists for sorting
        av_volt = [0] * 0
        av_spd = [0] * 0
        p2v = [0] * 0
        std = [0] * 0

        for i in range(2, len(datl)):
            splt = datl[i].split(",", 13)
            av_volt.append(float(splt[6]))
            av_spd.append(float(splt[12]))
            p2v.append(float(splt[0]))
            std.append(np.std(np.array([float(splt[7]), float(splt[8]), float(splt[9]), float(splt[10]), float(splt[11])])))

        av_speed_long = [0] * 0


        cur_pv = pv[0]
        pv_indx = 0
        for i in range(0, len(pv)):
            for j in range(0, len(p2v)):
                if (pv[i] - p2v[j]) < 8 and (pv[i] - p2v[j]) >= 0:

                    pv_indx = j
            av_speed_long.append(av_spd[pv_indx])

        rv_t_0 = [0] * 0
        rv_t_8 = [0] * 0
        rv_t_16 = [0] * 0
        rv_t_24 = [0] * 0
        rv_t_32 = [0] * 0
        rv_t_40 = [0] * 0
        rv_t_48 = [0] * 0
        rv_t_56 = [0] * 0
        rv_t_64 = [0] * 0
        rv_t_72 = [0] * 0
        rv_t_80 = [0] * 0
        rv_t_88 = [0] * 0
        rv_t_96 = [0] * 0
        rv_t_104 = [0] * 0
        rv_t_112 = [0] * 0
        rv_t_120 = [0] * 0
        rv_t_128 = [0] * 0

        av_rvs = np.array([0.0] * len(p2v))
        for i in range(0, len(pv)):
            for j in range(0, len(p2v)):
                if pv[i] == p2v[j]:
                    if j == 0 : rv_t_0.append(rv[i])
                    if j == 1 : rv_t_8.append(rv[i])
                    if j == 2 : rv_t_16.append(rv[i])
                    if j == 3 : rv_t_24.append(rv[i])
                    if j == 4 : rv_t_32.append(rv[i])
                    if j == 5 : rv_t_40.append(rv[i])
                    if j == 6 : rv_t_48.append(rv[i])
                    if j == 7 : rv_t_56.append(rv[i])
                    if j == 8 : rv_t_64.append(rv[i])
                    if j == 9 : rv_t_72.append(rv[i])
                    if j == 10 : rv_t_80.append(rv[i])
                    if j == 11 : rv_t_88.append(rv[i])
                    if j == 12 : rv_t_96.append(rv[i])
                    if j == 13 : rv_t_104.append(rv[i])
                    if j == 14 : rv_t_112.append(rv[i])
                    if j == 15 : rv_t_120.append(rv[i])
                    if j == 16 : rv_t_128.append(rv[i])

        # 2d list not working as expected, using manual (long hand) method :@
        stdv = [0] * 0

        # pv = 0
        stdv.append(np.std(rv_t_0))
        av_rvs[0] = np.average(rv_t_0)

        # pv = 8
        stdv.append(np.std(rv_t_8))
        av_rvs[1] = np.average(rv_t_8)

        # pv = 16
        stdv.append(np.std(rv_t_16))
        av_rvs[2] = np.average(rv_t_16)

        # pv = 24
        stdv.append(np.std(rv_t_24))
        av_rvs[3] = np.average(rv_t_24)

        # pv = 32
        stdv.append(np.std(rv_t_32))
        av_rvs[4] = np.average(rv_t_32)

        # pv = 40
        stdv.append(np.std(rv_t_40))
        av_rvs[5] = np.average(rv_t_40)

        # pv = 48
        stdv.append(np.std(rv_t_48))
        av_rvs[6] = np.average(rv_t_48)

        # pv = 56
        stdv.append(np.std(rv_t_56))
        av_rvs[7] = np.average(rv_t_56)

        # pv = 64
        stdv.append(np.std(rv_t_64))
        av_rvs[8] = np.average(rv_t_64)

        # pv = 72
        stdv.append(np.std(rv_t_72))
        av_rvs[9] = np.average(rv_t_72)

        # pv = 80
        stdv.append(np.std(rv_t_80))
        av_rvs[10] = np.average(rv_t_80)

        # pv = 88
        stdv.append(np.std(rv_t_88))
        av_rvs[11] = np.average(rv_t_88)

        # pv = 96
        stdv.append(np.std(rv_t_96))
        av_rvs[12] = np.average(rv_t_96)

        # pv = 104
        stdv.append(np.std(rv_t_104))
        av_rvs[13] = np.average(rv_t_104)

        # pv = 112
        stdv.append(np.std(rv_t_112))
        av_rvs[14] = np.average(rv_t_112)

        # pv = 120
        stdv.append(np.std(rv_t_120))
        av_rvs[15] = np.average(rv_t_120)

        # pv = 128
        stdv.append(np.std(rv_t_128))
        av_rvs[16] = np.average(rv_t_128)
            
        # 1st Trend: speed as a function of potval
        zavspdpv = np.polyfit(p2v[4:], av_spd[4:], 1)
        tlo = np.poly1d(zavspdpv)

        # Speed v Val  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
        # Set up figure
        f = plt.figure(figsize=(8, 8))
        ax = f.add_subplot(111)

        # 2nd Trend: read voltage as a function of potval
        z = np.polyfit(pv, rv, 1)
        tl = np.poly1d(z)

        # 3rd Trend: speed as a function of read voltage
        z3z = np.polyfit(tl(pv), tlo(pv), 1)
        return z3z[0], z3z[1]
        
if __name__ == "__main__":
    # init
    rows, columns = os.popen('stty size', 'r').read().split()
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    #plotwin = curses.newwin(int(0.2 * int(rows)), int(0.2 * int(rows)), 5, int(0.8 * int(rows)))
    plotwin = curses.newwin(25, 50, 5, 100)
    plotwin.border(0)
    if debug:
        mparams={'log_dir':'./','poll_logging':False}
    else:
        mparams={'log_dir':'./'}

    r = rheometer(motor_params=mparams)
    
    if debug:
        a = r.menutree()
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

    # Get list of strains
    #strains = np.linspace(5, 250, 128)
    
    # Get viscosity and show it to the user
    #print "Viscosity reading: {} Pa.s".format(r.get_viscosity(strains, 180))
    
