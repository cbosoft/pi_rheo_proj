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

    def __init__(self, length, **kwargs):
        #set defaults
        self.controller = PIDcontroller()
        self.mot_r = motor()
        self.pend_read = ADC()

        #process args
        for name, value in kwargs:
            if name == "control_Kp":
                self.controller.KP = value
            elif name == "control_Ki":
                self.controller.KI = value
            elif name == "control_Kd":
                self.controller.KD = value
            elif name == "control_sample_time":
                self.controller.sample_time = value
            elif name == "control_set_point":
                self.controller.set_point = value
            elif name == "motor_max_speed":
                self.mot_r.max_speed = value
            elif name == "motor_min_speed":
                self.mot_r.min_speed = value
            elif name == "motor_hall_pin":
                self.mot_r.hall_pin = value
            elif name == "motor_pot_addr":
                self.mot_r.pot.address = value
            elif name == "pend_address":
                self.pend_read.address = value
            elif name == "run_data_path":
                self.from_file(value)

        self.run_length = length

    def from_file(self, path):
        #dat file is a csv, path is [file_path]#[line_number]
        file_path = path[:(path.index('#'))]
        line_number = int(path[((path.index('#')) + 1):])
        f = open(file_path, "r")
        line = f.readlines()[line_number]
        f.close()
        vals = line.split(',')
        self.controller.KP = int(vals[0])
        self.controller.KI = int(vals[1])
        self.controller.KD = int(vals[2])
        self.controller.sample_time = int(vals[3])
        self.controller.set_point = int(vals[4])
        self.mot_r.max_speed = int(vals[5])
        self.mot_r.min_speed = int(vals[6])
        self.mot_r.hall_pin = int(vals[7])
        self.mot_r.pot.address = int(vals[8])
        self.pend_read.address = int(vals[9])

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
                outp = open(self.outp_path + "/rundat" + self.run_id +
                ".csv", "a")
            except IOError:
                os.mkdir(self.outp_path)
            outp = open(self.outp_path + "/rundat" + self.run_id + ".csv", "a")

            outp.write(str(time() * 1000) + "," + str(motor_speed) + ","
            + str(pend_value))

            outp.close()

            #if run is over:
            if (time() >= start_time + self.run_length):
                run_ongoing = False
        self.exit_clean()

    def exit_clean(self):
        self.mot_r.clean_exit()
