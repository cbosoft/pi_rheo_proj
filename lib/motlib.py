#
# motor.py
#
# allows the accurate control of a motor's speed from a raspberry pi
#

# imports
import time
import os
import thread as td
import RPi.GPIO as gpio
from glob import glob
from dig_pot import MCP4131 as dp
from adc import MCP3008 as ac


class motor(object):
    
    # Internal Switches
    poll_running = False  # is the speed currently being polled?
    
    # Logging
    poll_logging = True  # Will log every (i_poll_rate)s if this is True
    log_dir = "./dat+plot"  # where the logged data should be saved
    log_titles = ["Time", "Read Voltage", "Speed", "Current", "Pot val", "Power (electrical)"]
    i_poll_rate = 0.1  # How often data is polled, should not be less than span
    
    # Speed calc
    speed = 0.0  # Output value
    svf = [0.0, 0.0]  # 1st order linear fit equation; SPEED = svf[0] * VOLTAGE + svf[1]; VOLTAGE in volts, SPEED in RPM

    max_speed = 0  # RPM, at voltage = ~10.5v
    min_speed = 0  # RPM, at voltage = ~2.5v
    
    # Instances of Class
    pot = dp()  # potentiometer to control voltage
    aconv = ac()  # adc to read current/voltage
    adc_chan = [0, 1]  # voltage channel, current channel

    def __init__(self, max_speed=0, min_speed=0,
    startnow=False, adc_channels=[0, 1], adc_vref=3.3
    poll_logging=True, log_dir="./dat+plot",
    log_titles=["Time", "Read Voltage", "Speed", "Current", "Pot val", "Power (electrical)"],
    log_note="DATETIME"):

        # Set calibration variables
        self.max_speed = max_speed
        self.min_speed = min_speed

        # Set sensor variables
        self.pot = dp()
        self.aconv = ac(cs_pin=1, vref=adc_vref)
        
        # Set up logs
        self.log_dir = log_dir
        self.poll_logging = poll_logging
        self.new_logs(log_note)
        
        # Start speed polling (if necessary)
        if (startnow):
            self.start_poll(startnow)

    def new_logs(self, log_note="--"):
        # Try closing old log file
        try:
            logf.close()
        except:
            pass
        
        # Check if log directory exists. If not, create it.
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)

        # Get unique number for the log file
        un = time.strftime("%H %M %S", time.gmtime()) # str(len(glob(self.log_dir + "/*.csv")))

        # Creat logs (as necessary)
        if (self.poll_logging):
            self.logf = open(self.log_dir + "/log_" + un + ".csv", "w")
            for s in self.log_titles:
                self.logf.write(s + ", ")
            if (log_note == "DATETIME"):
                self.logf.write(time.strftime("%H:%M %d-%m-%Y", time.gmtime()) + "\n")
            else:
                self.logf.write("NOTE: " + log_note + "\n")

    def start_poll(self):
        if (not self.poll_running):  # if not already running
            td.start_new_thread(self.poll, tuple())

    def poll(self):

        self.poll_running = True

        while (self.poll_running):
            # self.get_power()  # get electrical power supplied to motor
            
            # Get speed
            volts = self.aconv.read_volts(self.adc_channels[0])
            self.speed = self.svf[0] * volts + self.svf[1]
            
            if (self.poll_logging):
                self.logf.write(("{0:.6f}, {1:.3f}, {2:.3f}, {3}, {4}, {5} \n").format(time.time(), volts, self.speed, "(current)", self.pot.lav, "(p = iv)"))
            
            # delay for x seconds
            time.sleep(self.i_poll_rate)

        print("Motor polling has halted.")

    def get_speed(self):
        if (self.poll_running):
            return self.speed
        else:
            print "Warning! Speed poll is not running, speed value is wrong."
            return 0.0

    def set_speed(self, speed):
        # check if speed value is in range
        value = speed
        if (value > self.max_speed):
            # value too big! warn + set to max speed
            print("Warning! Desired speed too high, setting to max speed.")
            value = self.max_speed
        elif (value < self.min_speed):
            # value too small! warn + set to min speed
            print("Warning! Desired speed too low, setting to min speed.")
            value = self.min_speed
        
        # convert speed value to a 7 bit number (0-127)
        value = int(((value - self.min_speed) /
        (self.max_speed - self.min_speed)) * 127)
        
        # Note: This assumes a perfectly linear variance of speed with resistance.
        # Will need to adjust this according to how the speed ACTUALLY varies with resistance.
        # If the variation is fairly unpredictable, then another system (incr/decr) will need to be used.
        # set this value on the digital potentiometer
        self.dp.set_resistance(value)

    def clean_exit(self):
        print "Closing poll thread..."
        self.poll_running = False
        time.sleep(0.5)
        
        if (self.poll_logging):
            print "Saving log file..."
            self.logf.close()

if __name__ == "__main__":
    #  Will get motor's speed for select potvals
    motr = motor(startnow=True, poll_logging=False)
    #test script for testing (plz don't use; its lazy, and bad form)
    try:
        for i in range(0, 128):
            motr.pot.set_resistance(i)
            print ("Speed (RPM): {0:.3f} val: {1}").format(motr.speed, motr.pot.lav)
            time.sleep(5)
    except KeyboardInterrupt:
        motr.clean_exit()
