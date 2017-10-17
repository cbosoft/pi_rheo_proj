'''
    Facilitates the control of a motor using dig_pot.py and adc.py.
    
    Controls the supply voltage sent to the motor in to control the speed.
    Data is logged using methods from adc.py. Noise is removed from the data
    using methods from filter.py. Temperature sensing data is obtained using
    tempsens.py.
    
    Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# System
import sys
import time
import os
import thread as td
from warnings import warn

# 3rd Party
try:
    import RPi.GPIO as gpio
except ImportError:
    import dummygpio as gpio
import numpy as np
#from PID import PID as pid

# RPi-R
#from filter import filter as ft
#from dig_pot import MCP4131 as dp
from adc import MCP3008 as ac
from control import pid_controller as pid
from tempsens import ds18b20 as ts
import dproc

class motor(object):
    '''
    Usage:
    
    object = motor.motor(**kwargs)
    
    Creates a new instance of a motor interface object.
    
    **kwargs:
        startnow        (bool)          Start polling as soon as the instance is created
        adc_vref        (float)         Voltage reference value. Default is 3.3
        poll_logging    (bool)          Indicates whether to log to file or not. Default is True.
        therm_sn        (string)        Serial number of the thermocouple. Used in 1-wire communication.
                                        Default is '28-0316875e09ff'
        i_poll_rate     (float)         Inverse poll rate: time to wait in between logging data. Default is 0.1
        pic_tuning      (float, float)  Tuning of PI controller. Kp and Ki respectively. Default is (0.2, 0.15)
        relay_pin       (integer)       Pin number which can be used to control the relay.
    '''
    # Logging
    poll_running = False  # is the speed currently being polled?
    poll_logging = True  # Will log every (i_poll_rate)s if this is True
    this_log_name = ""
    debug = False

    def __init__(self, startnow=False, adc_vref=3.3, poll_logging=True, therm_sn="28-0316875e09ff",
                 log_interval=0.01, tuning=(1.8, 2.845, 0.0), opt_pins=[16, 20, 21]):
        '''
        object = motor.motor(**kwargs)
        
        Creates a new instance of a motor interface object.
        
        **kwargs:
            startnow        (bool)          Start polling as soon as the instance is created. Default is False
            adc_vref        (float)         Voltage reference value. Default is 3.3
            poll_logging    (bool)          Indicates whether to log to file or not. Default is True.
            therm_sn        (string)        Serial number of the thermocouple. Used in 1-wire communication.
                                            Default is '28-0316875e09ff'
            i_poll_rate     (float)         Inverse poll rate: time to wait in between logging data. Default is 0.1
            pic_tuning      (float, float)  Tuning of PI controller. Kp and Ki respectively. Default is (0.2, 0.15)
            relay_pin       (integer)       Pin number which can be used to control the relay. Default is 18
        '''
        # Debug status string
        self.dss = ""

        # GPIO setup
        self.gpio_ready = False
        self.opt_pins = opt_pins
        self.setup_gpio()
        
        # controller
        self.pidc = pid(tuning)
        self.speed = 0.0
        self.control_stopped = True

        # Set sensor variables
        self.aconv = ac(cs_pin=1, vref=adc_vref)
        self.therm = ts(therm_sn)
        self.log_interval = log_interval
        self.volts = [0.0] * 8
        self.thermo_running = True
        self.temperature_c = 0.0
        self.temp_c_interval = 0.5
        
        # Set up logs
        self.poll_logging = poll_logging
        
        # Start threads
        if (startnow): self.start_poll(log_name)
        td.start_new_thread(self.thermometer, tuple())
    
    def setup_gpio(self):
        if self.gpio_ready: return
        # GPIO setup
        gpio.setmode(gpio.BCM)
        
        # Setup PWM pin
        self.pwm_pin = 18
        gpio.setup(self.pwm_pin, gpio.OUT)
        self.pwm_er = gpio.PWM(self.pwm_pin, 500)  # 0.5kHz
        self.ldc = 0.0
        self.pwm_er.start(0.0)
        
        # Setup optical encoder pins
        self.opt_pins = [21, 20]
        self.thens    = [time.time()] * (2 * len(self.opt_pins))
        self.rps      = [4.0] * len(self.opt_pins)
        self.speeds   = [0.0] * (len(self.opt_pins) * 2)
        self.misses   = [0] * len(self.opt_pins)
        self.t_misses = 10 # how many "incorrect" values to ignore before accepting
        
        for p in self.opt_pins:
            gpio.setup(p, gpio.IN, pull_up_down=gpio.PUD_UP)
            gpio.add_event_detect(p, gpio.BOTH, callback=self.opt_fr)
        gpio.setwarnings(False)
        self.gpio_ready = True

    def opt_fr(self, channel):
        now = time.time()
        dt = now - self.thens[channel]
        prov_spd = (60.0) / (dt * self.rps[channel]) # speed in rpm
        if ((prov_spd < (2 * self.speeds[channel])) or (self.misses[channel] > self.t_misses)):
            self.speeds[channel] = prov_spd
            self.misses[channel] = 0
        else:
            self.misses[channel] += 1
        self.thens[channel] = now
    
    def get_speed(self):
        return np.average(self.speeds)
        
    def thermometer(self):
        while (self.thermo_running):
            if self.therm.check_sn(): 
                self.temperature_c = self.therm.read_temp()
            else:
                self.thermo_running = False
            time.sleep(self.temp_c_interval)
        
    def new_logs(self, log_name="./../logs/log.csv"):
        '''
        motor.new_logs(**kwargs)
        
        Creates a new set of logs. Useful for running tests one after another.
        
        **kwargs:
            log_name        (string)            Indicates name of new log file.
        '''
        # Try closing old log file
        try:
            self.logf.close()
        except:
            pass

        # Create log
        if (self.poll_logging):
            self.this_log_name = str(log_name)
            self.logf = open(self.this_log_name, "w")
            self.logf.write("t,spd0,spd1,spd2,spd3,spd4,spd5,Vcr,adc0,dc,T,Vpz,Vms\n")

    def start_poll(self, name="./../logs/log.csv", controlled=False, debug_=False):
        '''
        motor.start_poll(**kwargs)
        
        Starts the data logging process. Launches a new thread which will continuously monitor the sensors and record
        the desired data. Saves file to <motor.log_dir>/<name>
        
        **kwargs:
            name            (string)            Indicates name of new log file. 'DATETIME' will be replaced by date
                                                and time of run. Default is 'DATETIME'
            controlled      (bool)              Indicates whether the control thread should be started or not.
        '''
        self.debug = debug_
        self.setup_gpio()
        if controlled: self.start_control()

        if self.poll_logging:
            self.new_logs(log_name=name)
        if (not self.poll_running):  # if not already running
            td.start_new_thread(self.poll, tuple())
    
    def start_control(self):
        '''
        motor.start_control()
        
        Starts the PI control of the speed. Launches a new thread which will use the control library to decide how to 
        alter the motor's supply voltage in order to maintain the setpoint.
        '''
        if self.control_stopped:
            self.control_stopped = False
            td.start_new_thread(self.control, tuple())
            
    def update_setpoint(self, value):
        '''
        motor.update_setpoint(value)
        
        Sets the new setpoint on the controller.
        
        Parameters:
            value       (float)         The strain value for the control system to target, (s^-1).
        '''
        self.pidc.set_point = value
    
    def control(self):
        '''
        motor.control()
        
        When motor.start_control() is called, a thread is created running this method. Continuously gets the speed 
        (filtered) from the sensor detection thread and calculates the control action (new motor supply voltage) to
        best maintain the setpoint.
        
        This will repeat until motor.control_stopped becomes True.
        '''
        while not self.control_stopped:
            av_speed = (np.average(self.r_speeds) + np.average(self.f_speeds)) / 2
            self.speed = av_speed
            av_speed = (2 * np.pi * av_speed) / 60.0
            self.speed_rads = av_speed
            control_action = self.pidc.get_control_action(dproc.get_strain(av_speed))
            #control_action = self.pidc.get_control_action(av_speed)
            if control_action > 100.0: control_action = 100.0
            if control_action < 0.0: control_action = 0
            self.set_dc(control_action)
            time.sleep(0.01)

    def read_sensors(self):
        '''
        motor.read_sensors()
        
        Reads from every channel of the ADC (CH0 to CH7).
        
        Returns:
            out     ([float] * 8)       List of values read from ADC.
        '''
        out = list()
        for a in range(0, 8):
            out.append(self.aconv.read_volts(a))
        return out
        
    def poll(self):
        '''
        motor.poll()
        
        When motor.start_poll() is called, a thread is created running this method. Continuously reads the sensors and 
        writes the values out to the log file.
        
        This will repeat until motor.stop_poll() is called, or motor.poll_running becomes False.
        '''
        self.poll_running = True
	
        while (self.poll_running):
            # At the third tone, the time will be...
            t = time.time()
            
            # Read sensors
            self.volts = self.read_sensors()
            
            if (self.poll_logging and not self.debug):
                #                   t       spd0   spd1    spd2    spd3    spd4    spd5    cra    adc0     dc      T     Vpz  Vms
                self.logf.write(("{:.6f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {:.3f}, {}, {:.3f} \n").format(
                    t, self.speeds[0], self.speeds[1], self.speeds[2], self.speeds[3], self.speeds[4], self.speeds[5], self.volts[2], self.volts[1], self.ldc, self.temperature_c, self.volts[4], (self.volts[7] * dproc.vmsmult)))
            elif (self.debug):
                self.logf.write(("{:.6f}, 80, 80, 80, 80, 80, 80, 3, 0, 50, 15, 2, 3 \n").format(t))
                    
            # delay for x seconds
            time.sleep(self.log_interval)
        self.clean_exit()

    def set_dc(self, value):
        '''
        motor.set_dc(value)
        
        Sets the duty cycle of the PWM - affecting the voltage supply to the motor.
        
        Parameters:
            value       (float)     Ratio of the 'high' part of the PWM signal to the
                                    'low' part. 100 is always on, 0 is never on.
        '''
        if value < 0.0:
            value = 0.0
        elif value > 100.0:
            value = 100.0
        
        self.ldc = value
        self.pwm_er.ChangeDutyCycle(value)
                   
    def clean_exit(self):
        '''
        motor.clean_exit()
        
        Cleanly shuts down sensor poll and control threads, as well as tidying up the GPIO settings and closing log 
        files.
        
        Should always be called when finished using the motor.
        '''
        # Halt threads
        self.poll_running = False
        self.control_stopped = True
        self.spf_needed = False
        self.thermo_running = False
        
        # Stop motor
        time.sleep(1)
        self.set_dc(0.0)
        time.sleep(2)
        self.set_dc(0.0)
        time.sleep(2)        
        
        # Release GPIO and whatnot
        self.pwm_er.stop()
        gpio.cleanup()
        self.gpio_ready = False
        
        # Close log files
        #self.opt_log.close()
        if (self.poll_logging):
            self.logf.close()

if __name__ == "__main__":
    print __doc__
    print motor.__doc__
