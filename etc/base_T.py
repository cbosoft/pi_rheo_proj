# System
from glob import glob
from copy import copy
import sys

# 3rd Party
import numpy as np
import scipy as sp
#from matplotlib import use as mpluse
#mpluse('Agg')  # can't remember this is here... fixes a bug perhaps?
import matplotlib.pyplot as plt

# RPi-R
sys.path.append("./../bin")
from plothelp import read_logf
from plothelp import fit_line
from filter import filter as filt_r
import resx

ln = "../logs/ccal_09.10.17-0944.csv"

print "Processing..."
print "\tLog: {}".format(ln)
try:
    __, st, f_spd0, r_spd0, f_spd1, r_spd1, f_spd2, r_spd2, cra, crb, Tc, Vpz, Vms, __, __, tag = read_logf(ln)
except KeyError:
    #old version of logs
    print "Something went wrong..."
    exit()

i_off = 0
i = 0
# lose unusable data
for j in range(len(st)):
    i = j - i_off
    if f_spd0[i] == 0 or f_spd1[i] == 0 or f_spd2[i] == 0 or r_spd0[i] == 0 or r_spd1[i] == 0 or r_spd2[i] == 0 or \
        f_spd0[i] > 4000 or f_spd1[i] > 4000 or f_spd2[i] > 4000 or r_spd0[i] > 4000 or r_spd1[i] > 4000 or r_spd2[i] > 4000:
        st = np.delete(st, i)
        f_spd0 = np.delete(f_spd0, i)
        r_spd0 = np.delete(r_spd0, i)
        f_spd1 = np.delete(f_spd1, i)
        r_spd1 = np.delete(r_spd1, i)
        f_spd2 = np.delete(f_spd2, i)
        r_spd2 = np.delete(r_spd2, i)
        cra = np.delete(cra, i)
        crb = np.delete(crb, i)
        Tc = np.delete(Tc, i)
        Vpz = np.delete(Vpz, i)
        Vms = np.delete(Vms, i)
        i_off += 1
if (len(st)) < 9:
    print "Too few data points"
    exit()

# Energy balance method calculation
omega   = list()
for i in range(0, len(f_spd1)):
     omega.append((f_spd0[i] + r_spd0[i] + f_spd1[i] + r_spd1[i] + f_spd2[i] + r_spd2[i]) / 6.0)
omega   = np.array(omega, np.float64)

current = resx.get_current(cra)

# Filtering!
voltage = filt_r(st, Vms)
omega   = filt_r(st, omega)
current = filt_r(st, current)

# Resistance measurements - lots because paranoid
R = np.average([15.9, 13.6, 16.4, 13.0, 13.3, 13.6, 13.6, 14.7, 15.4, 13.7, 16.4, 13.5, 17.4, 17.0])

# From datasheet: https://www.neuhold-elektronik.at/datenblatt/N7029.pdf
## NO LOAD
Vms_noload_V = 3.0
omega_noload_rpm = 3500
ke = Vms_noload_V / omega_noload_rpm

## STALL
Vms_stall_V = 3.0
omega_stall_rpm = 0
Ims_stall_A = 0.39
T_stall_Nm = 0.00251
kt = (T_stall_Nm * R) / Vms_stall_V

## MAX EFFICIENCY
T_maxeff_Nm = 0.00048
Vms_maxeff_V = 3.0
omega_maxeff_rpm = 2830.0
Ims_maxeff_A = 0.093
alt_kt = (T_maxeff_Nm * R) / (Vms_maxeff_V - (ke * omega_maxeff_rpm))

tol = 0.005
if ((1 - tol) * kt < alt_kt) and ((1 + tol) * kt > alt_kt):
    print "Calculated characteristic coefficients (+/- {} %)".format(tol * 100)
    print "\tke:", ke
    print "\tkt:", kt
else:
    print "Could not accurately calculate the motor characteristics!"
    exit()

T = kt * current

__, __, coeffs  = fit_line(omega, T, 2)
print coeffs

f = plt.figure()
plt.suptitle(ln)


fit = 0
for i in range(0, len(coeffs)):
    fit += coeffs[i] * (omega ** (len(coeffs) - 1 - i))


ax = f.add_subplot(111) #RCX
ax.plot(omega, T)
#ax.plot(omega, (np.e ** fit))
ax.plot(omega, fit)
plt.grid(axis="both")
ax.set_ylabel("T/Nm")

plt.show()
