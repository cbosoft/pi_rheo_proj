# plot helper
# useful defs for plotting
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from filter import filter
import resx

def fitf(x, a):
    return a * x


def fit_grad(x, y, number, x_name="x", y_name="y"):
    coeffs, __ = curve_fit(fitf, x, y)
    fit_eqn = r"${}\ =\ {:.4f} \times {}$".format(y_name, coeffs[0], x_name) 
    return fitf(x, *coeffs), fit_eqn, coeffs[0]


def fit_line(x, y, dg, x_name="x", y_name="y"):
    x = np.array(x)
    y = np.array(y)
    coeffs = np.polyfit(x, y, dg)
    fit = 0
    fit_eqn = "$fit:\ {} =".format(y_name)
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

def get_abs_sol_comp_unc(volA, volB, uncA, uncB):
    abs_err_vol_A = volA * uncA
    abs_err_tot_vol = (volA + volB) * (uncA + uncB)
    abs_err_vol_perc = abs_err_vol_A / abs_err_tot_vol
    return abs_err_vol_perc

def get_error(variable):
    # reading errors
    caliper_rerr_abs        = 0.0005        # plus or minus half a micrometer
    tachometer_rerr_abs     = 1
    ammeter_rerr_abs        = 0.005         # plus or minus 5 milliamps
    adc_rerr_perc           = 0.04888       # plus or minus 0.04888 percent of all ADC readings
    pipt_rerr_perc          = 0.3           # plus or minus 0.3 percent of the volume measured
    syringe_10_rerr_perc    = 1
    syringe_1_rerr_perc     = 1

    # other errors
    pipt_rerr_perc          = 1             # plus or minus 1 percent of the volume measured

    # propagated errors
    err_glyc_vol_9887_abs   = (29 * 0.01 * syringe_10_rerr_perc) + (0.62 * 0.01 * syringe_1_rerr_perc)
    err_wat_vol_9887_abs    = 0.38 * 0.01 * pipt_rerr_perc
    err_ref_9887_abs        = err_glyc_vol_9887_abs + err_wat_vol_9887_abs
    return get_abs_sol_comp_unc(29.62, 0.38, err_glyc_vol_9887_abs / 29.62, err_wat_vol_9887_abs / 0.38)


def read_logf(log_n):
    datf = pd.read_csv(log_n)
    
    t       =   np.array(datf['t'], np.float64)
    dr      =   np.array(datf['dr'], np.float64)
    cr      =   np.array(datf['cr'], np.float64)
    cr2a    =   np.array(datf['cr2a'], np.float64)
    cr2b    =   np.array(datf['cr2b'], np.float64)
    pv      =   np.array(datf['pv'], np.float64)
    fdr     =   np.array(datf['fdr'], np.float64)
    fcr     =   np.array(datf['fcr'], np.float64)
    T       =   np.array(datf['T'], np.float64)
    Vpz1    =   np.array(datf['Vpz1'], np.float64)
    Vpz2    =   np.array(datf['Vpz2'], np.float64)
    Vpzbg   =   [0.0] * len(t)
    Vadcbg  =   [0.0] * len(t)
    #Vpzbg   =   np.array(datf['Vpzbg'], np.float64)
    #Vadcbg  =   np.array(datf['Vadcbg'], np.float64)
    
    st = t - t[0]
    
    return t, st, dr, cr, cr2a, cr2b, pv, fdr, fcr, T, Vpz1, Vpz2, Vpzbg, Vadcbg

def simple_get_results(log_n):    
    t, st, dr, cr, cr2a, cr2b, pv, fdr, fcr, T, Vpz1, Vpz2, Vpzbg, Vadcbg = read_logf(log_n)
    
    voltage = 0.066 * pv + 2.422
    
    cu1     = resx.cal_30AHES[0] * cr + resx.cal_30AHES[1]
    cu2     = resx.cal_5AHES[0] * cr2a + resx.cal_5AHES[1]
    cu3     = resx.cal_5AHES[0] * cr2b + resx.cal_5AHES[1]
    current = (cu1 + cu2 + cu3) / 3
    
    power   = current * voltage
    
    current_base = resx.cal_IcoVms[0] * voltage + resx.cal_IcoVms[1]
    power_base   = voltage * current_base
    
    normal_visc  = power / power_base
    
    return normal_visc
    
def simple_plot(x, y, outp, xlab="", ylab="", leg=None):
    if leg == None: leg = [""]
    f = plt.figure()
    ax = f.add_subplot(111)
    ax.plot(x, y)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    plt.legend(leg)
    plt.savefig(outp)
    
def multi_plot(x, ys, outp, xlab="", ylab="", leg=None, filtering=False):
    if leg == None: leg = [""] * len(ys)
    f = plt.figure()
    ax = f.add_subplot(111)
    
    for y in ys:
        yp = y
        if filtering: yp = filter(x, y, method="butter", A=2, B=0.001)
        ax.plot(x, yp)
        
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    
    plt.legend(leg)
    plt.savefig(outp)
