#
# rheometer.py
#
# class object controlling the rheometer from the rasbperry pi
#

import time
import numpy as np
import pandas as pd

from motor import motor
from filter import filter
from plothelp import fit_line

class rheometer(object):
    
    # geometry
    roo     = 0.044151 / 2.0        # outer cell outer radius in m
    ro      = 0.039111 / 2.0        # outer cell radius in m
    ri      = 0.01525               # inner cell radius in m
    icxsa   = np.pi * (ri ** 2)     # inner cylinder XSA
    ocxsa   = np.pi * (ro ** 2)     # outer cylinder XSA
    dxsa    = ocxsa - icxsa         # vol per height in m3/m
    dxsa    = dxsa * 1000           # l / m
    dxsa    = dxsa * 1000           # ml / m
    fill_height = 0
    
    # empirical calibrations
    svf = [312.806, -159.196]
    spf = [5.13, 15.275]
    
    # classes
    mot = motor()
    
    def __init__(self, motor_params={'log_dir':'./rheometer'}, fill_vol=5):
        self.mot = motor(**motor_params)
        self.fill_height = fill_vol / self.dxsa
            
    def get_rheometry(self, strain_rate, run_length):
        pass
    
    def get_viscosity(self, strain_rate, run_length):
        variable_strain = True
        
        self.mot.start_poll()
        
        try:
            iterator = iter(strain_rate)
        except TypeError:
            variable_strain = False
        print "Reading data ({} s)...".format(run_length)
        try:
            if variable_strain:
                for i in range(0, len(strain_rate)):
                    self.set_strain_rate(strain_rate[i])
                    time.sleep(run_length / len(strain_rate))
            else:
                self.set_strain_rate(strain_rate)
                time.sleep(run_length)

            self.mot.clean_exit()
            print "Calculating viscosity..."
            return self.calc_visc(self.mot.this_log_name)

        except KeyboardInterrupt:
            self.mot.clean_exit()
            return 0  # Operation was cancelled

    def calc_visc(self, filename):
            datf = pd.read_csv(filename)

            # Split up csv columns
            t = datf['t']
            st = t - t[0]
            dr = datf['dr']
            cr = datf['cr']
            pv = datf['pv']
            
            # Fix out of range current readings
            for i in range(1, len(cr)):
                if cr[i] < 2.28: cr[i] = 2.28
                if cr[i] > 2.4: cr[i] = 2.4
            
            # Filtering: aye or naw?
            if True:
                dr = np.array(filter(st, dr, method="butter",A=2, B=0.001))
                cr = np.array(filter(st, cr, method="butter",A=2, B=0.001))
            
            # Calculate viscosity etc
            cu      = (-956.06 * (cr ** 3)) + (6543.97 * (cr ** 2)) + (-14924.369 * cr) + 11341.612
            sp_rpms = dr * 316.451 - 163.091
            sp_rads = (sp_rpms * 2 * np.pi) / 60
            sn_rpms = 5.13 * pv + 15.275
            vo      = 0.0636 * pv + 2.423
            pe      = cu * vo
            T       = 0.000001054 * pe - 0.000001488
            tau     = T / (2 * np.pi * self.ri * self.ri * self.fill_height) 
            gam_dot = (sp_rads * self.ri) / (self.ro - self.ri)
            
            #holy moses, more filtering?
            if False:
                tau     = filter(st, tau, method="butter", A=2, B=0.001)
                gam_dot = filter(st, gam_dot, method="butter", A=4, B=0.001)
            
            __, __, coeffs = fit_line(gam_dot, tau, 1)
            
            return coeffs[0]
            
    def set_strain_rate(self, value):
        desired_speed = value * (self.ro - self.ri) / self.ri  # in rads
        desired_speed = desired_speed * 60 / (2 * np.pi)  # in rpms
        if self.mot.control_stopped:
            set_pv = int((desired_speed - self.spf[1]) / self.spf[0])
            self.mot.set_pot(set_pv)
        else:
            self.mot.update_setpoint(desired_speed)

if __name__ == "__main__":
    # Create rheometer class instance
    r = rheometer(motor_params={'log_dir':'./rheometer'})
    
    # Get list of strains
    strains = np.linspace(5, 250, 128)
    
    # Get viscosity and show it to the user
    print "Viscosity reading: {} Pa.s".format(r.get_viscosity(strains, 180))
