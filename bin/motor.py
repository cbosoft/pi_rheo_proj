#
# motor.py
#
# allows the accurate control of a motor's speed from a raspberry pi
#

# imports
import sys
import time
import os
import thread as td
try:
    import RPi.GPIO as gpio
except ImportError:
    import dummygpio as gpio
import filter
from warnings import warn

#from glob import glob # Not necessary?
from dig_pot import MCP4131 as dp
from adc import MCP3008 as ac
from control import tf_pi_controller as pitf
from tempsens import ds18b20 as ts


class motor(object):
    
    # Internal Switches
    poll_running = False  # is the speed currently being polled?
    
    # Logging
    poll_logging = True  # Will log every (i_poll_rate)s if this is True
    log_paused = False
    log_add_note = False
    log_dir = "./logs"  # where the logged data should be saved
    i_poll_rate = 0.1  # How often data is polled, should not be less than span
    this_log_name = ""
    
    # Speed calc
    speed = 0.0  # Output value
    dr = 0.0
    fdr = 0.0
    svf = [300, -150]  # 1st order linear fit equation; SPEED = svf[0] * VOLTAGE + svf[1]; VOLTAGE in volts, SPEED in RPM
    
    # Filtering
    filtlen = 1000    # number of samples to "remember" for filtering purposes
    srvs = [0.0] * 0  # used to hold the last (filtlen) samples of dynamo volt readings
    crvs = [0.0] * 0  # used to hold the last (filtlen) samples of current volt readings
    tims = [0.0] * 0  # time data for ^
    filtering = "NONE"
    filter_delay = 100
    filtA = 2
    filtB = 0.008
    
    # Control thread
    control_stopped = True
    
    # Classes
    therm = ts("blank")
    pot = dp()  # potentiometer to control voltage
    pic = pitf((0.2, 0.15))
    aconv = ac()  # adc to read current/voltage
    adc_chan = [0, 1, 2, 3]  # voltage channel, current channel, current channel, current channel
    
    # GPIO Pins
    relay_pin = 0

    def __init__(self, startnow=False, adc_channels=[0, 1], adc_vref=3.3,
                 poll_logging=True, log_dir="./logs", therm_sn="28-0316875e09ff",
                 log_name="DATETIME", svf=[312.806, -159.196], i_poll_rate=0.1, pic_tuning=(0.2, 0.15),
                 filtering="NONE", filter_samples=100, filt_param_A=0.314, filt_param_B=0.314, relay_pin=0):

        # Set calibration variables
        self.svf = svf
        
        # Setup relay pin
        self.relay_pin = relay_pin
        gpio.setmode(gpio.BCM)
        gpio.setup(self.relay_pin, gpio.OUT)
        gpio.output(self.relay_pin, gpio.LOW)
        
        # controller
        self.pic = pitf(pic_tuning)
        
        # Filtering
        self.filtering = filtering
        if not filtering == "NONE": self.filtlen = filter_samples
        if not filt_param_A == 0.314: self.filtA = filt_param_A
        if not filt_param_B == 0.314: self.filtB = filt_param_B

        # Set sensor variables
        self.pot = dp()
        self.aconv = ac(cs_pin=1, vref=adc_vref)
        self.therm = ts(therm_sn)
        self.i_poll_rate=i_poll_rate
        
        # Set up logs
        self.log_dir = log_dir
        self.poll_logging = poll_logging
        
        # Start speed polling (if necessary)
        if (startnow): self.start_poll(log_name)

    def actuate(self):
        gpio.output(self.relay_pin, gpio.HIGH)
        
    def deactuate(self):
        gpio.output(self.relay_pin, gpio.LOW)
        
    def new_logs(self, log_name="DATETIME"):
        # Try closing old log file
        try:
            logf.close()
        except:
            pass
        
        # Check if log directory exists. If not, create it.
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)

        # Creat log
        if (self.poll_logging):
            if log_name == "DATETIME":
                # Get unique number for the log file
                un = time.strftime("%H %M %S", time.gmtime())
                self.this_log_name = self.log_dir + "/log_" + un + ".csv"
            else:
                #self.this_log_name = self.log_dir + "/" + log_name
                self.this_log_name = str(log_name)
            
            self.logf = open(self.this_log_name, "w")
            
            self.logf.write("t,dr,cr,cr2a,cr2b,pv,fdr,fcr,T\n")

    def log_pause(self):
        self.log_paused = True

    def log_resume(self, new_note="resumed"):
        self.log_note = new_note
        self.log_paused = False

    def start_poll(self, name="DATETIME"):
        if self.poll_logging:
            self.new_logs(log_name=name)
        if (not self.poll_running):  # if not already running
            td.start_new_thread(self.poll, tuple())
    
    def start_control(self):
        if self.control_stopped:
            self.control_stopped = False
            td.start_new_thread(self.control, tuple())
            
    def update_setpoint(self, value):
        self.pic.set_point = value
    
    def control(self):
        while not self.control_stopped:
            control_action = self.pic.get_control_action(self.speed)
            if control_action > 128: control_action = 128
            if control_action < 0: control_action = 0
            self.set_pot(control_action)
            time.sleep(0.1)
            
    def stop_control(self):
        self.control_stopped = True

    def read_sensors(self):
        return [self.aconv.read_volts(self.adc_chan[0]), self.aconv.read_volts(self.adc_chan[1]), self.aconv.read_volts(self.adc_chan[2]), self.aconv.read_volts(self.adc_chan[3])]
        
    def poll(self):

        self.poll_running = True
	
        while (self.poll_running):
            # At the third tone, the time will be...
            t = time.time()
            
            # Get speed
            self.volts = self.read_sensors()
            self.dr = self.volts[0]
            fvolts = self.volts

            # if desired, apply filtering to input
            if not (self.filtering == "NONE"):
                self.update_filt_hist(self.volts[0], self.volts[1], t)
                start_delay = 20

                #if self.filter_delay >= 100: start_delay = self.filter_delay + 1
                
                if (len(self.tims) >= start_delay):
                    fvolts[0] = filter.filter(self.tims, self.srvs, method=self.filtering, A=self.filtA, B=self.filtB)[-10]
                    fvolts[1] = filter.filter(self.tims, self.crvs, method=self.filtering, A=self.filtA, B=self.filtB)[-10]
            
            #print fvolts
            self.fdr = fvolts[0]
            self.speed = self.fdr * self.svf[0] + self.svf[1]
            
            temperature_c = 0.0
            # if thermosensor was set up properly...
            if self.therm.check_sn(): 
                temperature_c = self.therm.read_temp()
            else:
                warn("Temperature sensor cannot access its data! (Was the serial number entered correctly?)")
            
            if self.log_paused:
                self.log_add_note = True
            
            if (self.poll_logging) and (not self.log_paused):
                if self.log_add_note:
                    self.logf.write(("{0:.6f}, {1:.3f}, {2:.3f}, {7:.3f}, {8:.3f}, {3}, {4:.3f}, {5:.3f}, {9:.3f}, {6} \n").format(t, self.volts[0], self.volts[1], self.pot.lav, fvolts[0], fvolts[1], self.log_note, self.volts[2], self.volts[3], temperature_c))
                    self.log_add_note = False
                else:
                    self.logf.write(("{0:.6f}, {1:.3f}, {2:.3f}, {6:.3f}, {7:.3f}, {3}, {4:.3f}, {5:.3f}, {8:.3f} \n").format(t, self.volts[0], self.volts[1], self.pot.lav, fvolts[0], fvolts[1], self.volts[2], self.volts[3], temperature_c))
            
            # delay for x seconds
            time.sleep(self.i_poll_rate)

    def update_filt_hist(self, srv, crv, tim):
        if (len(self.srvs) + 1) > self.filtlen:
            self.srvs = self.srvs[1:]
            self.crvs = self.crvs[1:]
            self.tims = self.tims[1:]
        self.srvs.append(srv)
        self.crvs.append(crv)
        self.tims.append(tim)

    def set_pot(self, value):
        self.pot.set_resistance(int(value))
                   
    def clean_exit(self):
        self.poll_running = False
        self.control_stopped = True
        time.sleep(0.5)
        
        if (self.poll_logging):
            self.logf.close()

if __name__ == "__main__":
    #  Will get motor's speed for select potvals
    motr = motor(startnow=True, poll_logging=False, log_dir="./new_chip")
    #test script for testing (plz don't use; its lazy, and bad form)
    try:
        for i in range(0, 7):
            motr.pot.set_resistance(i*16)
            print ("Speed (RPM): {0:.3f} val: {1}").format(motr.speed, motr.pot.lav)
            time.sleep(5)
    except KeyboardInterrupt:
        motr.clean_exit()
