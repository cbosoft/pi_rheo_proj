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
    min_speed = 0  # RPM, at voltage = ~3v

    # GPIO pins
    hall_pin = 0

    pot = dp()

    def __init__(self, max_speed_=0, min_speed_=0, hall_pin_=0, pot_addr=0x5C, mag_count_=1, startnow=False):
        self.max_speed = max_speed_
        self.min_speed = min_speed_
        self.hall_pin = hall_pin_
        self.pot = dp()
        self.pot.address = pot_addr
        self.mag_count = mag_count_
        gpio.setmode(gpio.Board)
        gpio.setup(self.hall_pin, gpio.IN, pull_up_down = gpio.PUD_UP)
        
        if (startnow):
            self.start_poll()

    def start_poll(self):
        gpio.add_event_detect(self.hall_pin, gpio.RISING, callback=self.incr)
        if (not self.poll_running):
            td.start_new_thread(self.poll, tuple())

    def poll(self):

        self.poll_running = True

        while (self.poll_running):
            self.cur_speed = float(self.rot_count) * float(60 / (0.1 * self.mag_count))  # rotational speed in RPM
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
            print("Warning! Desired speed too high, setting to max speed.")
            value = self.max_speed
        elif (value < self.min_speed):
            # value too small! want + set to min speed
            print("Warning! Desired speed too low, setting to min speed.")
            value = self.min_speed
        value = int(((value - self.min_speed) / (self.max_speed - self.min_speed)) * 127)
        dp.set_resistance(value)

    def incr(self):
        self.rot_count += 1
    
    def clean_exit(self):
        gpio.cleanup()
        
if __name__ == "__main__":
    motr = motor(self, 0, 0, 16, 0x5C, 1, startnow=False)
    try:
        while (True):
            print "Speed (RPM) : " + str(motr.cur_speed)
            time.sleep(1)
    except KeyboardInterrupt:
        motr.clean_exit()

