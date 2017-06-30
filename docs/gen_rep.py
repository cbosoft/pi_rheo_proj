import sys
from glob import glob

sys.path.append("./../bin")

import plothelp as ph
from filter import filter as ft
import resx
import matplotlib
matplotlib.use('Agg')#
import matplotlib.pyplot as plt

## plot figures

############################################################################################################################
print "process latest log file"
log_files = sorted(glob("./../logs/rheometry*.csv"))
log_file = log_files[-1]
dt_ind = log_file[-15:-4]

short_date = dt_ind[0:6]
short_time = dt_ind[-4:]

long_date = "{}.{}.{}".format(short_date[:2], short_date[2:4], short_date[4:])
long_time = "{}:{}".format(short_time[0:2], short_time[2:])

############################################################################################################################
print "  reading log..."
t, st, dr, cr, cr2a, cr2b, pv, fdr, fcr, T, Vpz1, Vpz2, Vpzbg, Vadcbg, logtag = ph.read_logf(log_file)

############################################################################################################################
print "  plotting speed check"
speeds = resx.cal_dynamo[0] * dr + resx.cal_dynamo[1]
filt_speeds = ft(st, speeds, method="gaussian")

ph.multi_plot(st, [speeds, filt_speeds], "strain_check.png".format(dt_ind), xlab="Time, s", ylab="Speed, RPM", leg=["Raw", "Filtered"])

############################################################################################################################
print "  plotting rheometry check"
norm_visc = ph.simple_get_results(log_file)
norm_visc_filt = ft(st, norm_visc, method="gaussian")

ph.multi_plot(st, [norm_visc, norm_visc_filt], "viscometry.png".format(dt_ind), xlab="Time, s", ylab="Normalised Rheometry, unitless", leg=["Raw", "Filtered"])

############################################################################################################################
print "  plotting piezo results"
vraw = Vpz1
vcorr = vraw - Vpzbg - Vadcbg
#vcorr = vraw - Vpz2 # temp
vfilc = ft(t, vcorr, method="gaussian")

ph.multi_plot(st, [vraw, vcorr, vfilc], "./general_piezo.png".format(dt_ind), xlab="Time, s", ylab="Piezo (1) signal, V", leg=["Raw signal", "Corrected signal", "Corrected and filtered signal"])

############################################################################################################################
print "  plotting overall comparison"
ph.multi_multi_plot(st, [filt_speeds / filt_speeds[-1], norm_visc_filt / norm_visc_filt[-1], vfilc / vfilc[-1], pv], "norm_signal_compare.png".format(dt_ind), xlab="Time, s", ylab=["Speed (Norm'd)", "Viscosity (Norm'd)", "Piezo Voltage (Norm'd)", "Strain (Norm'd)"], leg=["Speeds", "Viscosity", "Piezo", "Strain"])

ph.multi_multi_plot(st, [filt_speeds, norm_visc_filt, vfilc, pv], "signal_compare.png".format(dt_ind), xlab="Time, s", ylab=["Speed, RPM", "Viscosity Ref", "Piezo Voltage, V", "Strain Ref"], leg=["Speeds", "Viscosity", "Piezo", "Strain"])

############################################################################################################################
l = 10 # number of logs to try to compare
if len(log_files) < l: l = len(logs)
print "comparing last {} logs".format(l)

f = plt.figure(figsize=(8,8))
ax = f.add_subplot(111)

leg = list()
for f in log_files[-(l + 1):-1]:
    print "  plotting {}".format(f)
    t, st, dr, cr, cr2a, cr2b, pv, fdr, fcr, T, Vpz1, Vpz2, Vpzbg, Vadcbg, tag = ph.read_logf(f)
    leg.append(tag)
    vraw = Vpz1
    vcorr = vraw - Vpzbg - Vadcbg
    vfilc = ft(t, vcorr, method="gaussian")
    
    #ax.plot(st, vraw, color=(0, 0, 1, 0.75))
    #ax.plot(st, vcorr, color=(0, 0, 1, 0.5))
    ax.plot(st, vfilc)

ax.set_xlabel("Time, s")
ax.set_ylabel("Piezo signal, V")
plt.legend(leg)
plt.savefig("./logs_piezo_compare.png")


############################################################################################################################
print "writing tex report"
templ_f = open("./auto_rep_template.tex", "r")
templ_l = templ_f.readlines()
templ_f.close()

for i in range(0, len(templ_l)):
    templ_l[i] = templ_l[i].replace("VERSION", resx.version)
    templ_l[i] = templ_l[i].replace("DATE", long_date)
    templ_l[i] = templ_l[i].replace("TIME", long_time)
    templ_l[i] = templ_l[i].replace("X", "{}".format(l))
    templ_l[i] = templ_l[i].replace("LOGTAG", logtag)

rep_f = open("./auto_rep.tex", "w")
rep_f.writelines(templ_l)
rep_f.close()