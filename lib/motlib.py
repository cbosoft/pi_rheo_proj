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
import filter
from glob import glob
from dig_pot import MCP4131 as dp
from adc import MCP3008 as ac


class motor(object):
    
    # Internal Switches
    poll_running = False  # is the speed currently being polled?
    
    # Logging
    poll_logging = True  # Will log every (i_poll_rate)s if this is True
    log_paused = False
    log_add_note = False
    log_dir = "./dat+plot"  # where the logged data should be saved
    log_titles = ["Time/s", "Dynamo Reading/V", "HES Reading/V", "Potentiometer Value/7-bit" "Filtered Dynamo Reading/V"]
    i_poll_rate = 0.1  # How often data is polled, should not be less than span
    this_log_name = ""
    
    # Speed calc
    speed = 0.0  # Output value
    svf = [1.0, 0.0]  # 1st order linear fit equation; SPEED = svf[0] * VOLTAGE + svf[1]; VOLTAGE in volts, SPEED in RPM
    
    # Filtering ## Separate filter for current reading?
    filtlen = 500  # number of samples to "remember" for filtering purposes
    srvs = [0.0] * 0  # used to hold the last (filtlen) samples of dynamo volt readings
    crvs = [0.0] * 0  # used to hold the last (filtlen) samples of current volt readings
    tims = [0.0] * 0  # time data for ^
    filtering = "NONE"
    filter_delay = 100

    # Current calc
    current = 0.0 # Read current in A
    cvf = [1.0, 0.0]  # 1st order linear fit equation; CURRENT = cvf[0] * VOLTAGE + cvf[1]; VOLTAGE in volts, CURRENT in Amps

    max_speed = 0  # RPM, at voltage = ~10.5v
    min_speed = 0  # RPM, at voltage = ~2.5v
    
    # Instances of Class
    pot = dp()  # potentiometer to control voltage
    aconv = ac()  # adc to read current/voltage
    adc_chan = [0, 1]  # voltage channel, current channel

    def __init__(self, max_speed=0, min_speed=0,
    startnow=False, adc_channels=[0, 1], adc_vref=3.3,
    poll_logging=True, log_dir="./dat+plot",
    log_titles=["Time/s", "Dynamo Reading/V", "HES Reading/V", "Potentiometer Value/7bit", "Filtered Dynamo Reading/V", "Filtered HES Reading/V"],
    log_note="DATETIME", svf=[317.666, -146.947], cvf=[1.0, 0.0], i_poll_rate=0.1,
    filtering="NONE", filter_samples=100):

        # Set calibration variables
        self.max_speed = max_speed
        self.min_speed = min_speed
        self.svf = svf
        self.cvf = cvf
        
        # Filtering
        if filtering == "NONE":
            self.filtering = "NONE" 
        else:
            self.filtering = filtering
        
        if not filtering == "NONE": self.filtlen = filter_samples

        # Set sensor variables
        self.pot = dp()
        self.aconv = ac(cs_pin=1, vref=adc_vref)
        self.i_poll_rate=i_poll_rate
        
        # Set up logs
        self.log_dir = log_dir
        self.log_titles = log_titles
        self.poll_logging = poll_logging
        self.new_logs(log_note)
        
        # Start speed polling (if necessary)
        if (startnow):
            self.start_poll()

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

        # Creat log
        if (self.poll_logging):
            self.this_log_name = self.log_dir + "/log_" + un + ".csv"
            self.logf = open(self.this_log_name, "w")
            for s in self.log_titles:
                self.logf.write(s + ", ")
            if (log_note == "DATETIME"):
                self.logf.write(time.strftime("%H:%M %d-%m-%Y", time.gmtime()) + "\n")
            else:
                self.logf.write("NOTE: " + log_note + "\n")

    def start_poll(self):
        if (not self.poll_running):  # if not already running
            td.start_new_thread(self.poll, tuple())

    def log_pause(self):
        self.log_paused = True

    def log_resume(self, new_note="resumed"):
        self.log_note = new_note
        self.log_paused = False

    def poll(self):

        self.poll_running = True

        while (self.poll_running):
            # self.get_power()  # get electrical power supplied to motor
            
            # At the third tone, the time will be...
            t = time.time()
            
            # Get speed
            volts = [self.aconv.read_volts(self.adc_chan[0]), self.aconv.read_volts(self.adc_chan[1])]
            fvolts = volts
            self.speed = self.svf[0] * volts[0] + self.svf[1]
            # if desired, apply filtering to input
            if not (self.filtering == "NONE"):
                self.update_filt_hist(volts[0], volts[1], t)
                
                start_delay = 100

                if self.filtering_delay >= 100: start_delay = filtering_delay + 1
                    
                if (len(self.tims) >= start_delay):
                    fvolts[0] = filter.filter(self.tims, self.srvs, method=self.filtering)[-self.filter_delay]
                    fvolts[1] = filter.filter(self.tims, self.crvs, method=self.filtering)[-self.filter_delay]
                else:
                    volts= [0, 0]
            
            # Get current
            # self.current = self.cvf[0] * volts[1] + self.cvf[1]
            
            # Power = Current x Supply Voltage
            # Supply voltage is calculable from the potentiometer value (POTVAL/127) * (10.5 - 2.8) + 2.8 = SUPPLY VOLTAGE
            # self.power = (((self.pot.lav / 127) * (10.5 - 2.8)) + 2.8) * self.current
            if self.log_paused:
                self.log_add_note = True

            if (self.poll_logging) and (not self.log_paused):
                if self.log_add_note:
                    self.logf.write(("{0:.6f}, {1:.3f}, {2:.3f}, {3}, {4:.3f}, {5:.3f}, {6} \n").format(t, volts[0], volts[1], self.pot.lav, fvolts[0], fvolts[1], self.log_note))
                    self.log_add_note = False
                else:
                    self.logf.write(("{0:.6f}, {1:.3f}, {2:.3f}, {3}, {4:.3f}, {5:.3f} \n").format(t, volts[0], volts[1], self.pot.lav, fvolts[0], fvolts[1]))
            
            # delay for x seconds
            time.sleep(self.i_poll_rate)

        print("Motor polling has halted.")

    def update_filt_hist(self, srv, crv, tim):
        if (len(self.spds) + 1) > self.filtlen:
            self.srvs = self.srvs[1:]
            self.crvs = self.crvs[1:]
            self.tims = self.tims[1:]
        self.srvs.append(srv)
        self.crvs.append(crv)
        self.tims.append(tim)

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
    
    def fix_logs(self):
        logf = open(self.this_log_name, "r")
        datl = logf.readlines()
        logf.close()

        cols = [[0] * 0] * 0
        for i in range(0, len(self.log_titles)):
            cols.append([self.log_titles[i]] * 1)
        cols.append(["notes\n"] * 1)

        for i in range(1, len(datl)):
            splt = datl[i].split(",", len(self.log_titles))
            for j in range(0, len(cols)):
                cols[j].append(splt[j])

        for i in range(0, len(cols)):
            if cols[i][0][:4] == "Filt":
                title = cols[i][0]
                mv = cols[i][1:self.filter_delay + 1]
                main_data = cols[i][self.filter_delay + 1:]
                cols[i] = [title]*1
                for j in range(0, len(main_data)):
                    cols[i].append(main_data[j])
                for j in range(0, len(mv)):
                    cols[i].append(mv[j])

        logf = open(self.this_log_name, "w")
        for i in range(0, len(cols[0])):
            line = ""
            for j in range(0, len(cols)):
                line += (str(cols[j][i]) + ",")
            logf.write(line[:-1])
        logf.close()
                   
    def clean_exit(self):
        print "Closing poll thread..."
        self.poll_running = False
        time.sleep(0.5)
        
        if (self.poll_logging):
            print "Saving log file..."
            self.logf.close()
            
            if not self.filtering == "NONE":
                self.fix_logs()

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
