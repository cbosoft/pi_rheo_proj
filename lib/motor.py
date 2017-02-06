#
# motor.py
#
# allows the accurate control of a motor's speed from a raspberry pi
#

# imports
import time
import thread as td
import RPi.GPIO as gpio
from dig_pot import MCP4131 as dp
from adc import MCP3424 as ac


class motor(object):

    cur_speed = 0.0
    cur_speed_other = 0.0
    prev_hit_time = 0.0
    mag_count = 1
    poll_running = False
    rot_count = 0
    log_dir = "./log.csv"

    max_speed = 0  # RPM, at voltage = 11v
    min_speed = 0  # RPM, at voltage = ~3v

    # GPIO pins
    hall_pin = 0

    pot = dp()
    aconv = ac()

    def __init__(self, max_speed_=0, min_speed_=0, hall_pin_=0, mag_count_=1,
    startnow=False, adc_addr=0x6E, adc_channel=0, adc_rate=0, adc_gain=2):
        self.max_speed = max_speed_
        self.min_speed = min_speed_
        self.hall_pin = hall_pin_
        self.pot = dp()
        #self.aconv = ac(adc_addr, adc_channel, adc_rate, adc_gain)
        self.mag_count = mag_count_
        gpio.setmode(gpio.BOARD)
        gpio.setup(self.hall_pin, gpio.IN, pull_up_down=gpio.PUD_UP)

        if (startnow):
            self.start_poll()

    def start_poll(self):
        gpio.add_event_detect(self.hall_pin, gpio.RISING, callback=self.incr)
        if (not self.poll_running):
            td.start_new_thread(self.poll, tuple())

    def poll(self):

        self.poll_running = True
        self.logf = open(self.log_dir, "w")

        while (self.poll_running):
            pass
            #self.mot_current = self.aconv.read_data()
            # alt speed get algo
            # self.cur_speed = (float(self.rot_count)
            # * float(60) / (float(0.1) * float(self.mag_count))))  # rotational speed in RPM
            # self.rot_count = 0
            # time.sleep(0.1)

        print("Motor polling has halted.")
        self.logf.close()

    def get_speed(self):
        if (self.poll_running):
            return self.cur_speed
        else:
            print "Warning! Speed poll is not running, speed value is wrong."
            return 0.0

    def set_speed(self, speed):
        # convert speed to 7bit number (0 to 127)
        value = speed
        if (value > self.max_speed):
            # value too big! warn + set to max speed
            print("Warning! Desired speed too high, setting to max speed.")
            value = self.max_speed
        elif (value < self.min_speed):
            # value too small! warn + set to min speed
            print("Warning! Desired speed too low, setting to min speed.")
            value = self.min_speed
        value = int(((value - self.min_speed) /
        (self.max_speed - self.min_speed)) * 127)
        self.dp.set_resistance(value)

    def incr(self, channel):
        self.rot_count += 1
        temp_time = time.time() * 1000
        if (self.prev_hit_time == 0.0):
            pass
        else:
            self.cur_speed_other = 60000 / (self.mag_count * (temp_time - self.prev_hit_time))
            # rotations per hit (R/hit) / time per hit (ms/hit) = rotations per time (R/ms)
            # (R/ms) * 60,000 = RPM
        self.prev_hit_time = temp_time
        self.logf.write(str(time.time()) + ", " + str(self.rot_count) + ", " + str(self.cur_speed_other) + "\n")

    def clean_exit(self):
        print "Closing poll thread..."
        self.poll_running = False
        time.sleep(0.5)
        gpio.cleanup()
        self.logf.close()
        # self.pot.close()

if __name__ == "__main__":
    #  motor(max_speed, min_speed, hall_pin, mag_count, start_now)
    #  Will get motor's speed for select potvals
    motr = motor(0, 0, 16, 1, startnow=True)
    #test script for testing
    try:
        for i in range(0, 128):
            for j in range(0, 10):
                print "Speed (RPM): " + str(motr.cur_speed_other)
                time.sleep(0.5)
    except KeyboardInterrupt:
        motr.clean_exit()
