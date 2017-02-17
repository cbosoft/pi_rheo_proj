#
# motor.py
#
# allows the accurate control of a motor's speed from a raspberry pi
#

# imports
import time
import thread as td
import RPi.GPIO as gpio
from glob import glob
from dig_pot import MCP4131 as dp
from adc import MCP3424 as ac


class motor(object):
    
    # Outputs
    prev_hit_time = 0.0  # Used to calculate the speed of the motor - time the hall last had a hit
    rot_count_last = 0  # Last value of the rot count before speed_avish was calculated
    prev_span_time = 0.0  # Time of previous span speed calc
    speed_insta = 0.0  # Speed taken from a single sample, closest to actual instant speed
    speed_avish = 0.0  # Speed taken from a number of samples, almost instant speed but is average
    rot_count = 0  # number of magnet hits counted (total)
    
    # Internal Switches
    poll_running = False  # is the speed currently being polled?
    waiting = False  # used to increase the accuracy of the sensor
    
    # Misc Settings
    mag_count = 1  # number of magnets on the motor's rotor
    
    # Logging
    input_logging = False  # Will record pseudo waveform when True
    poll_logging = True  # Will log if this is True
    log_dir = "./dat+plot"  # where the logged data should be saved
    log_titles = ["Time", "Rev Count", "Speed (Tick)", "Speed (Span)", "ADC val", "Pot val"]

    # Speed Calc Settings
    per_tick = True  # Calculates speed every time the hall pin registers a rotation (or partial), using time between ticks
    per_span = False  # Calculates speed every x second, using number of rotations in that time 
    span = 1.0  # x above -> How often the average speed is calculated (smaller time, more instant, less average)
    i_poll_rate = 0.1  # How often data is polled, should not be less than span

    max_speed = 0  # RPM, at voltage = ~10.5v
    min_speed = 0  # RPM, at voltage = ~2.5v

    # GPIO pins
    hall_pin = 16  # normally board pin 16, GPIO 23
    
    # Instances of Class
    pot = dp()  # potentiometer to control voltage
    # aconv = ac()  # adc to read current/voltage
    # adc_chan = [1, 2]  # voltage channel, current channel

    def __init__(self, max_speed=0, min_speed=0, hall_pin=0, mag_count=1,
    startnow=False, adc_addr=0x6E, adc_channel=0, adc_rate=0, adc_gain=2,
    input_logging=True, poll_logging=True, log_dir="./dat+plot",
    log_titles=["Time", "Rev Count", "Speed (Tick)", "Speed (Span)", "ADC val", "Pot val"],
    log_note="DATETIME"):

        # Set calibration variables
        self.max_speed = max_speed
        self.min_speed = min_speed

        # Set sensor variables
        self.hall_pin = hall_pin
        self.pot = dp()
        #self.aconv = ac(adc_addr, adc_channel, adc_rate, adc_gain)
        self.mag_count = mag_count

        # Set up GPIO
        gpio.setmode(gpio.BOARD)
        gpio.setup(self.hall_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        
        # Set up logs
        self.new_logs(log_note)

        if (startnow):
            self.start_poll()

    def new_logs(self, log_note="--"):
        # Try closing old log files
        try:
            logf.close()
            logh.close()
        except:
            pass
        
        # Check if log directory exists. If not, create it.
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)

        # Get unique number for the log file
        un = str(len(glob(self.log_dir + "/*.csv")))

        # Creat logs (as necessary)
        if (self.poll_logging):  # Poll log: every (i_poll_rate) seconds, info is logged.
            self.logf = open(self.log_dir + "/log_" + un + ".csv", "w")
            for s in self.log_titles:
                self.logf.write(s + ", ")
            if (log_note == "DATETIME"):
                self.logf.write(time.strftime("%H:%M %d-%m-%Y", time.gmtime())
            else:
                self.logf.write("NOTE: " + self.log.note + "\n")

        if (self.input_logging):  # Input log: every time a revolution is detected, the time this occurs is recorded.
            self.logh = open(self.log_dir + "/log_" + "hall_" + un + ".csv", "w")  # log file is called "hall" for historically reasons

    def start_poll(self):
        gpio.add_event_detect(self.hall_pin, gpio.RISING, callback=self.incr)  # When the GPIO pin is first risen to a high level, the method "incr(self, channel)" is called
        gpio.add_event_detect(self.hall_pin, gpio.FALLING, callback=self.unwait)  # When the GPIO pin falls back to a low level, the method "unwait(self, channel" is called

        if (not self.poll_running):
            td.start_new_thread(self.poll, tuple())

    def poll(self):

        self.poll_running = True

        while (self.poll_running):
            # self.get_power()  # get electrical power supplied to motor
            
            dspan = time.time() - self.prev_span_time
            if (self.prev_span_time == 0):
                self.prev_span_time = time.time()  # set initial span time
            elif (self.per_span and dspan >= self.span):
                # Calculate speed
                self.cur_speed = (float(self.rot_count - self.rot_count_last)
                 * float(60) / (float(dspan) * float(self.mag_count)))  # rotational speed in RPM
                self.prev_span_time = time.time()
                self.rot_count_last = self.rot_count

            if (self.poll_logging):
                #self.logf.write(str(time.time()) + ", " + str(self.rot_count) + ", " + str(self.speed_insta) + ", " + str(self.speed_avish) + ", " + str(self.aconv.read_single()) + ", " + str(self.pot.lav) + "\n")
                self.logf.write(("{0:.6f}, {1}, {2:.3f}, {3:.3f}, {4}, {5} \n").format(time.time(), self.rot_count, self.speed_insta, self.speed_avish, self.aconv.read_single(), self.pot.lav)  # maybe take new epoch since 1485907200 (1st feb 2017) to reduce data to write?
            time.sleep(i_poll_rate)

        print("Motor polling has halted.")

    def get_speed(self):
        if (self.poll_running):
            return self.speed_avish  # or speed_insta?
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

    def incr(self, channel):
        if not waiting:
            self.rot_count += 1
            temp_time = time.time() * 1000.0
            if (self.per_tick and self.prev_hit_time != 0.0):
                self.speed_insta = float(60000) / (float(self.mag_count) * (temp_time - self.prev_hit_time))
                # rotations per hit (R/hit) / time per hit (ms/hit) = rotations per time (R/ms)
                # (R/ms) * 60,000 = RPM

            if (self.input_logging):
                self.logh.write(("{0:.3f} \n").format(temp_time))
            self.prev_hit_time = temp_time
            self.waiting = True

    def unwait(self, channel):
        self.waiting = False  # sensor will not register any more hits until this is called

    def clean_exit(self):
        print "Closing poll thread..."
        self.poll_running = False
        time.sleep(0.5)
        
        print "Tidying GPIO..."
        gpio.cleanup()
        
        if (self.poll_logging):
            print "Saving log file..."
            self.logf.close()
        if (self.input_logging):
            self.logh.close()
        
        # print "Closing SPI connection..."
        # self.pot.close()

if __name__ == "__main__":
    #  motor(max_speed, min_speed, hall_pin, mag_count, start_now)
    #  Will get motor's speed for select potvals
    motr = motor(0, 0, 16, 1, startnow=True, adc_gain=0)
    #test script for testing (plz don't use; its lazy, and bad form)
    try:
        for i in range(0, 128):
            motr.pot.set_resistance(i)
            for j in range(0, 10):
                print ("Speed (RPM): {0:.3f} val: {1}").format(motr.speed_insta, motr.pot.lav)
                time.sleep(0.5)
    except KeyboardInterrupt:
        motr.clean_exit()
