# plot helper
# useful defs for plotting
import numpy as np
from scipy.optimize import curve_fit

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


svf_raw = [308.768, -167.080]
cvf1_raw = [15.93, -28.59]
cvf2_raw = [11.07, -28.44]
vsvf_raw = [0.066, 2.278]

def svf(val):
    return svf_raw[0] * val + svf_raw[1]

def cvf1(val):
    return cvf1_raw[0] * val + cvf1_raw[1]

def cvf2(val):
    return cvf2_raw[0] * val + cvf2_raw[1]

def vsvf(val):
    return vsvf_raw[0] * val + vsvf_raw[1]
