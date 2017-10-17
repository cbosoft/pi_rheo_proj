'''
dproc.py

Provides data about the rheometer (geometry etc) as well as methods useful in data processing 
and plotting

Provides run-time access to the information stored in the /etc/data.xml file, including access 
to calibrations and the geometry of the cylinders.

Also has a few functions that allow the easy use of the calibrations ("get_supply_voltage(pv)" 
for example)

Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# System
import math
from copy import copy

# 3rd Party
import xml.etree.ElementTree as ET
import numpy as np
from numpy import *
from scipy.optimize import curve_fit
try:
    import spidev # will error if not on rpi
    from matplotlib import use as mpluse
    mpluse('Agg')  # for plotting from commandline (with no xserver or anything)
except:
    pass # not on rpi, don't need to use (!xserver) as gui backend
import matplotlib.pyplot as plt
import pandas as pd

# RPi-R
from filter import filter


# read the xml file
root = ET.parse('./../etc/data.xml').getroot()

def parse_root(name, type):
    global root
    for child in root:
        # can be geometry or calibration...
        if child.tag == type and type == "geometry":
            if child.attrib["name"] == name:
                return float(child[0].text)
        elif child.tag == type and type == "calibration":
            if child.attrib["name"] == name:
                return [float(child[0].text), float(child[1].text)]
        elif child.tag == type and type == "misc":
            if child.attrib["name"] == name:
                return child[0].text

######################################################################################################################## XML VARS
icor = parse_root("icor", "geometry")
ich = parse_root("ich", "geometry")
ocor = parse_root("ocor", "geometry")
ocir = parse_root("ocir", "geometry")
och = parse_root("och", "geometry")

cal_dynamo = parse_root("dynamo", "calibration")
cal_5AHES = parse_root("5AHES", "calibration")

cal_IcoVms = parse_root("IcoVms", "calibration")
cal_TsVms = parse_root("TsVms", "calibration")
cal_TIemf = parse_root("TIemf", "calibration")

version = parse_root("version", "misc")

######################################################################################################################## GLOBALS/runtime
vmsmult = 4.0 # due to voltage divider taking motor supply voltage down to a level the ADC can read

# Noload/maxeff/stall values taken from datasheet: https://www.neuhold-elektronik.at/datenblatt/N7029.pdf
## NO LOAD
Vms_noload_V = 3.0
omega_noload_rpm = 3500
omega_noload_rads = omega_noload_rpm * (2.0 * np.pi / 60.0)

## STALL
Vms_stall_V = 3.0
Ims_stall_A = 0.39
T_stall_Nm = 0.00251

## MAX EFFICIENCY
T_maxeff_Nm = 0.00048
Vms_maxeff_V = 3.0
omega_maxeff_rpm = 2830.0
omega_maxeff_rads = omega_maxeff_rpm * (2.0 * np.pi / 60.0)
Ims_maxeff_A = 0.093

# Resistance measurements - lots because paranoid
R = np.average([15.9, 13.6, 16.4, 13.0, 13.3, 13.6, 13.6, 14.7, 15.4, 13.7, 16.4, 13.5, 17.4, 17.0])

## Calculate kv
kv_noload = Vms_noload_V / omega_noload_rads
kv_stall = (T_stall_Nm * R) / Vms_stall_V
kv = np.average([kv_noload, kv_stall])

## Get mass of inner cylinder
rho_nylon = 1150.0 # kg/m3
m_cyl_b = rho_nylon * (icor ** 2) * ich
m_cyl_t = rho_nylon * 2 * (0.01 ** 3)
m_cyl = m_cyl_b + m_cyl_t

######################################################################################################################## XML FUNCTIONS
def writeout(path="./../etc/data.xml"):
    '''
    writeout(**kwargs)
    
    Writes the contents of a data file.
    
    **kwargs:
        path        (string)        Path to data.xml. Default is './../etc/data.xml'
    '''
    global root
    # update xml tree
    
    # geometries
    root[0][0].text = str(icor)
    root[1][0].text = str(ich)
    root[2][0].text = str(ocor)
    root[3][0].text = str(ocir)
    root[4][0].text = str(och)
    root[5][0].text = version
    # calibrations
    root[6][0].text = str(cal_dynamo[0])
    root[6][1].text = str(cal_dynamo[1])
    root[8][0].text = str(cal_5AHES[0])
    root[8][1].text = str(cal_5AHES[1])
    root[9][0].text = str(cal_IcoVms[0])
    root[9][1].text = str(cal_IcoVms[1])
    root[10][0].text = str(cal_TIemf[0])
    root[10][1].text = str(cal_TIemf[1])
    
    tree = ET.ElementTree(root)
    tree.write(path)

######################################################################################################################## VISCOSITY CALCULATION STUFF
def get_mu_of_T(material_n, T_c, misc_data=None):
    '''
    get_mu_of_T(material_n, T_c, misc_data=None
    
    Uses functions from various data sources in order to calculate continuously
    the viscosity data of various compounds and mixtures from the current temperature.
    
    Parameters
    ----------
    
    material_n      (string)            The name of the material to calculate the viscosity for.
                                        Can also be a definition of a mixture e.g. 'glycerol+water'
                                        the '+' character is necessary, and all mixture definitions
                                        must follow the same formula.
    
    T_c             (float/iterable)    The temperature(s) in celsius used to calculate the
                                        viscosity of the material.
    
    misc_data       (float/string)      For mixtures, there is often required to be extra information
                                        to calculate the viscosity - such as the composition.
                                        This can be set here depending on the function requirements.
    
    Returns
    -------
    
    mu_out          (float)             The viscosity of the specified material/mixture
    
    References
    ----------
    
    [Cheng 2008]    "Formula for the Viscosity of a Glycerol-Water Mixture",
                    Nian-Sheng Cheng, Ind. Eng. Chem. Res. 2008, 47, 3285-3288
    '''
    
    materials_dict = {
    
        "glycerol":0,
        
        "water":1,
        
        "glycerol+water":2
        
        }
    
    function_index = 0
    
    try:
        function_index = materials_dict[material_n]
    except:
        raise Exception("Material not known! Did you spell it correctly?")
    
    # Alternative T units
    T_K = T_c + 273.15                  # Tabs, Kelvin
    T_F = T_c * (9.0/5.0) + 32.0        # Trel, Fahrenheit
    T_R = T_F + 459.67                  # Tabs, Rankine
    
    mu_out = 0.0
    
    if function_index == 0:
        # Material is glycerol
        #
        # Function is taken from [Cheng 2008]
        mu_out = ((12100.0 * (e ** (((-1232.0 + T_c) * T_c) / (9900.0 + (70.0 * T_c))))) * 0.001)
    elif function_index == 1:
        # Material is water
        #
        # Function is taken from [Cheng 2008]
        mu_out = ((1.79 * (e ** (((-1230.0 - T_c) * T_c) / (36100.0 + (360.0 * T_c))))) * 0.001)
    elif function_index == 2:
        # Material is aqueous glycerol solution
        #
        # Method is taken from [Cheng 2008]
        a = (0.705 - 0.0017 * T_c)
        b = ((4.9 + 0.036 * T_c) * (a ** 0.25))
        mug = ((12100.0 * (e ** (((-1232.0 + T_c) * T_c) / (9900.0 + (70.0 * T_c))))) * 0.001)
        muw = ((1.79 * (e ** (((-1230.0 - T_c) * T_c) / (36100.0 + (360.0 * T_c))))) * 0.001)
        cm = float(misc_data)
        alpha = (1.0 - cm + ((a * b * cm * (1.0 - cm)) / ((a * cm) + (b * (1.0 - cm)))))
        mu_out = (muw ** alpha) * (mug ** (1.0 - alpha))
    return mu_out

def get_current(cv):
    cu = ((cv - 2.5) / 0.185) # current = (signal - (2.5v offset)) * (0.185 v/A sensitivity)
    return cu

def get_strain(omega_rads):
    '''
    get_strain(omega)

    Parameters:
        dr      (list, float)       [List of] dynamo voltage readings.
    
    Returns:
        gd      (list, float)       [List of] strains in inverse seconds.
    '''
    gd = omega_rads * (icor / (ocir - icor)) 
    return gd

def get_stress(T, fill_volume_ml):
    A_small = (pi * (icor ** 2)) # in m^2
    A_big   = (pi * (ocir ** 2)) # in m^2
    A_middle_m2 = A_big - A_small
    fill_volume_m3 = fill_volume_ml * (10.0 ** (-6.0)) # 1000 ml in a l, 1 000 l in a m3: 10^6ml in a m3
    H = fill_volume_m3 / A_middle_m2
    stress = T / (2 * A_small * H)
    return stress

def calc_mu(st, Vms_V, Ims_A, fill_volume_m3, omega_rads, dwdt_override=None):
    gamma_dot = get_strain(omega_rads)
    a = 1
    tau = 0
    T = 0
    try:
        a = len(st)
        domegadt = [0]
        for i in range(1, a):
            domegadt.append((omega_rads[i] - omega_rads[i - 1]) / (st[i] - st[i - 1]))
        
        domegadt = np.array(domegadt, np.float64)
            
        T = list()
        for i in range(a):
            T.append(kv * Ims_A[i] - (m_cyl * 0.5 * (icor ** 2) * domegadt[i]))
         
        T = np.array(T, np.float64)
    except TypeError:
        if dwdt_override:
            domegadt = dwdt_override
        else:
            domegadt = 0
            
        T = kv * Ims_A - (m_cyl * 0.5 * (icor ** 2) * domegadt)
    tau = get_stress(T, fill_volume_m3)
    mu = tau / gamma_dot
    return gamma_dot, T, tau, mu

######################################################################################################################## PLOT STUFF
def fit_line(x, y, dg, x_name="x", y_name="y"):
    '''
    fit_line(x, y, dg, **kwargs)
    
    Fits a polynomial to a data series.
    
    Parameters:
        x       (list, float)       X data.
        y       (list, float)       Y data.
        dg      (integer)           Order of the polynomial function to fit.
    
    **kwargs:
        x_name  (string)            Symbol to use for the 'x' series, will be used to create 
                                    a string representation of the resulting polynomial. Default is x
        y_name  (string)            Symbol to use for the 'y' series, will be used to create 
                                    a string representation of the resulting polynomial. Default is y
    
    Returns:
        fit     (???)               No idea to be honest. I wrote this function almost six months ago.
        fit_eqn (string)            A clean representation of the polynomial fit. Intended to be inserted
                                    into a matplotlib plot as part of the legend or some such. 
                                    Uses 'LaTeX' formatting.
        coeffs  (list, float)       A list of the coefficients of the polynomial fit, in decending powers.
    '''
    x = np.array(x)
    y = np.array(y)
    coeffs = np.polyfit(x, y, dg)
    fit = 0
    fit_eqn = "$\\rmfit:\ {} =".format(y_name)
    cf_str = ""
    for i in range(0, len(coeffs)):
        fit += coeffs[i] * (x ** (len(coeffs) - 1 - i))
        if i == 0:
            cf_str = "({:.3E})".format(coeffs[i])
        elif coeffs[i] < 0:
            cf_str = "-({:.3E})".format(-1*coeffs[i])
        else:
            cf_str = "+({:.3E})".format(coeffs[i])
        if (len(coeffs) - 1 - i) > 1:
            fit_eqn += " {} \\times {}^{}".format(cf_str, x_name, "{" + str((len(coeffs) - 1 - i)) + "}")
        elif (len(coeffs) - 1 - i) == 1:
            fit_eqn += " {} \\times {}".format(cf_str, x_name)
        else:
            fit_eqn += " {}".format(cf_str)

    fit_eqn += "$"
    return fit, fit_eqn, coeffs

def plot_fit(x, y, dg, x_name="x", y_name="y", outp="./test.png"):
    fit, fit_eqn, coeffs = fit_line(x, y, dg, x_name="x", y_name="y")
    f = plt.figure()
    ax = plt.gca()
    ax.plot(x, y, "x", label="{}({})".format(y_name, x_name))
    ax.plot(x, fit, label=fit_eqn)
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name)
    plt.legend()
    plt.savefig(outp)
    return fit, fit_eqn, coeffs

class LogTooShortError(Exception):
    '''Occurs when the log is too short to provide any meaningful data (<9 values)'''
    
    def __str__(self):
        return "Log too short :("

def read_logf(log_n, strip_outliers=False, strip_0speed=False, filter_readings=False, f0_is_omega_rpm=False, cra_is_Ims_A=False, dia=False):
    '''
    read_logf(log_n)
    
    Reads a .csv log file and outputs the columns as numpy arrays (float64).
    '''
    if dia:
        strip_outliers = True
        strip_0speed = True
        filter_readings = True
        f0_is_omega_rpm = True
        cra_is_Ims_A = True
        
    datf = pd.read_csv(log_n)
    
    t         =   np.array(datf['t'], np.float64)
    spd0      =   np.array(datf['spd0'], np.float64)
    spd1      =   np.array(datf['spd1'], np.float64)
    spd2      =   np.array(datf['spd2'], np.float64)
    spd3      =   np.array(datf['spd3'], np.float64)
    spd4      =   np.array(datf['spd4'], np.float64)
    spd5      =   np.array(datf['spd5'], np.float64)
    Vcr       =   np.array(datf['Vcr'], np.float64)
    adc0      =   np.array(datf['adc0'], np.float64)
    Vms       =   np.array(datf['Vms'], np.float64)
    Tc        =   np.array(datf['Tc'], np.float64)
    Vpz       =   np.array(datf['Vpz'], np.float64)
    
    try:
        tau       =   np.array(datf['tau'], np.float64)
        gamma_dot =   np.array(datf['gamma_dot'], np.float64)
    except:
        tau       = [0] * len(t)
        gamma_dot = [0] * len(t)
    
    st = t - t[0]
    
    if strip_outliers:
        # do nothing at the moment, but will remove data points that are out of scope or whatever
        pass
    if strip_0speed:
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
    if filter_readings:
        f_spd0 = filter(st, f_spd0)
        r_spd0 = filter(st, r_spd0)
        f_spd1 = filter(st, f_spd1)
        r_spd1 = filter(st, r_spd1)
        f_spd2 = filter(st, f_spd2)
        r_spd2 = filter(st, r_spd2)
        Vms = filter(st, Vms)
        cra = filter(st, cra)
    if f0_is_omega_rpm:
        for i in range(len(f_spd0)):
            f_spd0[i] = np.average([f_spd0[i], r_spd0[i], f_spd1[i], r_spd1[i], f_spd2[i], r_spd2[i]])
        r_spd0 = f_spd0 * (2.0 * np.pi / 60)
    if cra_is_Ims_A:
        cra = (cra - 2.5) / 0.185
    if len(f_spd0) <= 9: raise LogTooShortError
    
    return t, st, spd0, spd1, spd2, spd3, spd4, spd5, Vcr, adc0, Tc, Vpz, Vms, gamma_dot, tau, "na"
    

def get_significant_minimums(y, sens=10):
    '''
    get_significant_minimums(y, **kwargs)
    
    Gets the most significantly minimum values of a dataseries.
    
    Parameters:
        y       (list, float)       List of y-values.
    
    **kwargs:
        sens    (integer)           Sensitivity; what percentage of (average y value) 
                                    constitutes significantly lower.
                                    
    Returns:
        res     (list, integer)     List of indexes of the points at which the Y value 
                                    is more than [sens]% lower than the average magnitude 
                                    of the y-values.
    '''
    
    av = np.average(y)
    
    diff = (sens / 100.0) * math.fabs(av)
    
    res = list()
    
    is_descending = False
    
    for i in range(1, len(y)):
        if y[i] < y[i - 1]:
            is_descending = True
        elif y[i] >= y[i - 1] and is_descending:
            is_descending = False
            if y[i] < (av - diff):
                res.append(i)
    return res
    
    
if __name__ == "__main__": print __doc__
