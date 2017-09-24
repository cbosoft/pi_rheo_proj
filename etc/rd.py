from glob import glob

import numpy as np

from plothelp import plot_fit
from plothelp import read_logf
import resx

I_EMFs = list()
T_MSs  = list()

ref_logs = glob("./../logs/mcal*")

for i in range(0, len(ref_logs)):
    print "Calculating...",
    print "    {}".format(ref_logs[i])
              
    __, st, __, __, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, T, Vpz, Vms, gamma_dot, tau, tag = read_logf(ref_logs[i])
    
    # mcal_[name]_[viscosity]_pas_[date+time].csv
    viscosity = float(ref_logs[i].split('_')[2])
    print "\tFluid: ", ref_logs[i].split('_')[1]
    print "\tViscosity: ", viscosity
    I_MS = resx.get_current(cra)
    I_CO = resx.get_current_coil(Vms)
    I_EMF = [0.0] * len(I_MS)
    for j in range(0, len(I_MS)):
        I_EMF[j] = I_MS[j] - I_CO[j]
    I_EMFs.append(np.average(I_EMF))
            
    stress = viscosity * np.average(gamma_dot)
    torque = resx.get_torque(stress, 15)
    print "\tStress:   ", stress
    print "\tStrain:   ", np.average(gamma_dot)
    print "\tTorque:   ", torque
    print "\tI emf :   ", I_EMFs[-1]
    T_MSs.append(torque)

__, f_eqn, mot_cal = plot_fit(I_EMFs, T_MSs, 1, x_name="Iemf", y_name="Tau")
print "New fit:"
print "\tTau = Iemf * {} + {}".format(mot_cal[0], mot_cal[1])
