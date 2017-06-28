import sys
from glob import glob

sys.path.append("./../bin")

import plothelp as ph
from filter import filter as ft
import resx

## plot figures

# get log file to plot
log_file = sorted(glob("./../logs/rheometry*.csv"))[-1]
dt_ind = log_file[-15:-4]

short_date = dt_ind[0:6]
short_time = dt_ind[-4:]

long_date = "{}.{}.{}".format(short_date[:2], short_date[2:4], short_date[4:])
long_time = "{}:{}".format(short_time[0:2], short_time[2:])

# read csv
t, st, dr, cr, cr2a, cr2b, pv, fdr, fcr, T, Vpz1, Vpz2, Vpzbg, Vadcbg = ph.read_logf(log_file)

# 1st plot
speeds = resx.cal_dynamo[0] * dr + resx.cal_dynamo[1]
filt_speeds = ft(st, speeds, method="gaussian")

ph.multi_plot(st, [speeds, filt_speeds], "strain_check.png".format(dt_ind), xlab="Time, s", ylab="Speed, RPM", leg=["Raw", "Filtered"])

# 2nd plot - rheometry check
norm_visc = ph.simple_get_results(log_file)
norm_visc_filt = ft(st, norm_visc, method="gaussian")

ph.multi_plot(st, [norm_visc, norm_visc_filt], "viscometry.png".format(dt_ind), xlab="Time, s", ylab="Normalised Rheometry, unitless", leg=["Raw", "Filtered"])

# 3rd plot - piezo check
vraw = Vpz1
vcorr = vraw - Vpzbg - Vadcbg
#vcorr = vraw - Vpz2 # temp
vfilc = ft(t, vcorr, method="gaussian")

ph.multi_plot(st, [vraw, vcorr, vfilc], "./general_piezo.png".format(dt_ind), xlab="Time, s", ylab="Piezo (1) signal, V", leg=["Raw signal", "Corrected signal", "Corrected and filtered signal"])

# 4th plot - overall check
ph.multi_multi_plot(st, [filt_speeds / filt_speeds[-1], norm_visc_filt / norm_visc_filt[-1], vfilc / vfilc[-1], pv], "norm_signal_compare.png".format(dt_ind), xlab="Time, s", ylab=["Speed (Norm'd)", "Viscosity (Norm'd)", "Piezo Voltage (Norm'd)", "Strain (Norm'd)"], leg=["Speeds", "Viscosity", "Piezo", "Strain"])

ph.multi_multi_plot(st, [filt_speeds, norm_visc_filt, vfilc, pv], "signal_compare.png".format(dt_ind), xlab="Time, s", ylab=["Speed, RPM", "Viscosity Ref", "Piezo Voltage, V", "Strain Ref"], leg=["Speeds", "Viscosity", "Piezo", "Strain"])
## create report tex

templ_f = open("./auto_rep_template.tex", "r")
templ_l = templ_f.readlines()
templ_f.close()

for i in range(0, len(templ_l)):
    templ_l[i] = templ_l[i].replace("VERSION", resx.version)
    templ_l[i] = templ_l[i].replace("DATE", long_date)
    templ_l[i] = templ_l[i].replace("TIME", long_time)

rep_f = open("./auto_rep.tex", "w")
rep_f.writelines(templ_l)
rep_f.close()

## then process report file...