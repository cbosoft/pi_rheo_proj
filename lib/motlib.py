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

    # Two methods. First doesn't work but should...
    # Second also doesn't work, but is less broken that the first.
    cur_speed = 0.0
    cur_speed_other = 0.0
    
    # Globals
    prev_hit_time = 0.0  # Used to calculate the speed of the motor - time the hall last had a hit
    mag_count = 1  # number of magnets on the motor's rotor
    poll_running = False  # is the speed currently being polled?
    rot_count = 0  # number of magnet hits counted (total)
    rot_count_last = 0
    
    # Logging
    hall_debug_logging = False  # Will record pseudo waveform when True
    poll_logging = True  # Will log if this is True
    log_dir = "./dat+plot"  # where the logged data should be saved
    log_titles = ["Time", "Rev Count", "Speed (Tick)", "Speed (Span)", "ADC val", "Pot val"]
    log_note = ""

    # Speed calc methdos
    per_tick = True  # Calculates speed every time the hall pin registers a click, using time between ticks
    per_span = False  # Calculates speed every x second, using number of rotations in that time 
    span = 1.0  # x above
    tick = 0.1
    span_time_last = 0.0

    max_speed = 0  # RPM, at voltage = 11v
    min_speed = 0  # RPM, at voltage = ~3v

    # GPIO pins
    hall_pin = 0
    
    # Instances of Class
    pot = dp()  # potentiometer to control voltage
    aconv = ac()  # adc to read current/voltage
    adc_chan = [1, 2]  # voltage channel, current channel

    def __init__(self, max_speed_=0, min_speed_=0, hall_pin_=0, mag_count_=1,
    startnow=False, adc_addr=0x6E, adc_channel=0, adc_rate=0, adc_gain=2):
        self.max_speed = max_speed_
        self.min_speed = min_speed_
        self.hall_pin = hall_pin_
        self.pot = dp()
        self.aconv = ac(adc_addr, adc_channel, adc_rate, adc_gain)
        self.mag_count = mag_count_
        gpio.setmode(gpio.BOARD)
        gpio.setup(self.hall_pin, gpio.IN, pull_up_down=gpio.PUD_UP)
        self.new_logs()

        if (startnow):
            self.start_poll()

    def new_logs(self):
        # Close old log files
        try:
            logf.close()
            logh.close()
        except:
            pass

        # Get unique name for the log file
        un = str(len(glob(self.log_dir + "/*.csv")))

        # Creat logs (as necessary)
        if (self.poll_logging):
            self.logf = open(self.log_dir + "/log_" + un + ".csv", "w")
            for s in self.log_titles:
                self.logf.write(s + ", ")
            self.logf.write("NOTE: " + self.log.note + "\n")

        if (self.hall_debug_logging):
            self.logh = open(self.log_dir + "/log_" + "hall_" + un + ".csv", "w")

    def start_poll(self):
        gpio.add_event_detect(self.hall_pin, gpio.RISING, callback=self.incr)
        if (not self.poll_running):
            td.start_new_thread(self.poll, tuple())

    def poll(self):

        self.poll_running = True

        while (self.poll_running):
            # self.get_power()  # get electrical power supplied to motor
            
            dspan = time.time() - self.span_time_last
            if (self.span_time_last == 0):
                self.span_time_last = time.time()
                # set initial span time
            elif (self.per span and dspan >= self.span):
                # Calculate speed
                self.cur_speed = (float(self.rot_count - self.rot_count_last)
                 * float(60) / (float(dspan) * float(self.mag_count)))  # rotational speed in RPM
                self.span_time_last = time.time()
                self.rot_count_last = self.rot_count
            
            #if ((time.time() * 1000) - self.prev_hit_time) > 100:
                #self.cur_speed = 0
            #    self.cur_speed_other = 0 
            if (self.poll_logging):
                self.logf.write(str(time.time()) + ", " + str(self.rot_count) + ", " + str(self.cur_speed_other) + ", " + str(self.cur_speed) + ", " + str(self.aconv.read_single()) + ", " + str(self.pot.lav) + "\n")
            time.sleep(tick)

        #print("Motor polling has halted.")

    def get_speed(self):
        if (self.poll_running):
            return self.cur_speed
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
        self.rot_count += 1
        temp_time = time.time() * 1000.0
        if (self.per_tick and self.prev_hit_time != 0.0):
            self.cur_speed_other = float(60000) / (float(self.mag_count) * (temp_time - self.prev_hit_time))
            # rotations per hit (R/hit) / time per hit (ms/hit) = rotations per time (R/ms)
            # (R/ms) * 60,000 = RPM

        if (self.hall_debug_logging):
            self.logh.write(str(temp_time) + "\n")
        self.prev_hit_time = temp_time

    def clean_exit(self):
        print "Closing poll thread..."
        self.poll_running = False
        time.sleep(0.5)
        
        print "Tidying GPIO..."
        gpio.cleanup()
        
        if (self.poll_logging):
            print "Saving log file..."
            self.logf.close()
        if (self.hall_debug_logging):
            self.logh.close()
        
        # print "Closing SPI connection..."
        # self.pot.close()

if __name__ == "__main__":
    #  motor(max_speed, min_speed, hall_pin, mag_count, start_now)
    #  Will get motor's speed for select potvals
    motr = motor(0, 0, 16, 1, startnow=True, adc_gain=0)
    #test script for testing
    try:
        for i in range(0, 128):
            motr.pot.set_resistance(i)
            for j in range(0, 10):
                print "Speed (RPM): " + str(motr.cur_speed_other) + " val: " + str(motr.pot.lav)
                time.sleep(0.5)
    except KeyboardInterrupt:
        motr.clean_exit()
