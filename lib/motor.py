#
# motor.py
#
# allows the accurate control of a motor's speed from a raspberry pi
#

# imports
import time
import thread as td
import RPi.GPIO as gpio
from dig_pot import mcp4531 as dp


class motor(object):

    cur_speed = 0.0
    mag_count = 1
    poll_running = False
    rot_count = 0

    max_speed = 0  # RPM, at voltage = 11v
    min_speed = 0  # RPM, at voltage = ~4v

    # GPIO pins
    hall_pin = 0

    pot = dp()

    def __init__(self, max_speed_, min_speed_, hall_pin_, pot_addr=0x5C, mag_count_=1, startnow=False):
        self.max_speed = max_speed_
        self.min_speed = min_speed_
        self.hall_pin = hall_pin_
        self.pot = dp()
        self.pot.address = pot_addr
        self.mag_count = mag_count_

        if (startnow):
            self.start_poll()

    def start_poll(self):
        gpio.add_event_detect(self.hall_pin, gpio.FALLING, callback=self.incr)
        if (not self.poll_running):
            td.start_new_thread(self.poll, tuple())

    def poll(self):
        time_start = 0
        delta_time = 0

        self.poll_running = True

        while (self.poll_running):
            if (time_start == 0):
                time_start = int(round(time.time() * 1000))  # in milliseconds

            delta_time = int(round(time.time() * 1000)) - time_start  # delta time in milliseconds

            if (delta_time >= 100):
                self.cur_speed = float(self.rot_count / (self.mag_count * delta_time * 60))  # rotational speed in RPM
                time_start = 0
                self.rot_count = 0

            time.sleep(0.1)

        print("Motor speed polling has halted!")

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
            print("Desired speed too high! setting to max speed.")
            value = self.max_speed
        elif (value < self.min_speed):
            # value too small! want + set to min speed
            print("Desired speed too low! setting to min speed.")
            value = self.min_speed
        value = int(((value - self.min_speed) / (self.max_speed - self.min_speed)) * 127)
        dp.set_reg(value)

    def incr(self):
        self.rot_count += 1