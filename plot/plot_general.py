import sys
from glob import glob

sys.path.append("./../bin")

import plothelp as ph
from filter import filter as ft

# get log file to plot

log_files = sorted(glob("./../logs/rheometry*.csv"))

for log_file in log_files:
    t, st, dr, cr, cr2a, cr2b, pv, fdr, fcr, T, Vpz1, Vpz2, Vpzbg, Vadcbg = ph.read_logf(log_file)
    
    vraw = Vpz1
    vcorr = vraw - Vpzbg - Vadcbg - Vpz2
    vfilc = ft(t, vcorr, method="gaussian")
    
    ph.multi_plot(st, [vraw, vcorr, vfilc], "./general_piezo_{}.png".format(log_file[-15:-4]), xlab="Time, s", ylab="Piezo (1) signal, V", leg=["Raw signal", "Corrected signal", "Corrected and filtered signal"])
