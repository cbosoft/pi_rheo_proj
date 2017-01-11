#
# Master Class
#
# Class for running an experiment with the raspberry pi:
#    will monitor, record, and set a motor's speed
#    will read and record the input from a piezo
#

# Imports
from adc import mcp3424 as ADC
from control import PIDcontroller
from motor import motor
from time import time
import os


class run(object):

    outp_path = "outp"

    run_id = "R001"

    run_start = 0

    run_length = 0

    def __init__(self, Kp, Ki, Kd, sample_tim, setpnt, max_spd, min_spd, hall_pin, pot_address, magnet_count, ad_c, length):

        self.controller = PIDcontroller(Kp, Ki, Kd, sample_tim, setpnt)

        self.mot_r = motor(max_spd, min_spd, hall_pin, pot_address, magnet_count)

        self.pend_read = ADC(0x6e, 0, 0, 0)

        self.run_length = length

    def start_run(self):

        self.mot_r.start_poll()

        try:
            self.loop()
        except KeyboardInterrupt:
            self.exit_clean()

    def loop(self):

        motor_speed = 0
        pend_value = 0

        start_time = time()

        #initialise timer
        time_of_last = int(round(time() * 1000))

        run_ongoing = True

        while (run_ongoing):
            # set time since last iteration
            time_since_last = int(round(time() * 1000)) - time_of_last

            # if enough time has passed, get control action and apply it
            if (time_since_last >= (self.controller.sample_time * 1000)):
                motor_speed = self.mot_r.get_speed()  # speed in RPM
                delta_spd = self.controller.get_control_action(motor_speed)
                self.mot_r.set_speed(motor_speed + delta_spd)

            # get pend value
            pend_value = self.pend_read.get_volts()

            # append csv with time, motor speed, pend value
            try:
                outp = open(self.outp_path + "/rundat" + self.run_id + ".csv", "a")
            except IOError:
                os.mkdir(self.outp_path)
            outp = open(self.outp_path + "/rundat" + self.run_id + ".csv", "a")

            outp.write(str(time() * 1000) + "," + str(motor_speed) + "," + str(pend_value))
            outp.close()

            #if run is over:
            if (time() >= start_time + self.run_length):
                run_ongoing = False
            self.exit_clean()

    def exit_clean():
        pass