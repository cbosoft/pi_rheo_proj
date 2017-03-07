#
# From a list of responses, gets time span between responses and forms a histogram
#
import matplotlib.pyplot as plt
import numpy as np
from glob import glob

def histo(log_path, out_fig, xlabel, ylabel, colour="blue"):
    #Read logfile (light sensor)
    datf = open(log_path, "r")
    datl = datf.readlines()
    datf.close()

    #maximum number of lines to process from data (for looking at specific sections)
    maxlen = 100000000000
    lento = len(datl)
    if (maxlen < lento):
        lento = maxlen

    
    # Create lists
    t = [0] * lento  # Time
    st = [0] * lento  # Specific time (time from start of run, not epoch)
    dt = [0] * lento  # Time between measurements (should be fairly constant)

    # Split data into lists for easy use
    for i in range(0, lento):
        splt = datl[i].split(",", 5)
        t[i] = float(splt[0])

        if (i == 0):
            st[i] = 0
            dt[i] = 0
        else:
            st[i] = t[i] - t[0]
            dt[i] = t[i] - t[i - 1]

    # Plot Data
    f = plt.figure(figsize=(7, 7))
    ax1 = f.add_subplot(111)

    # Bins might need tweaking between datasets
    bins = np.linspace(-5, 10, 16)

    (n, b, patches) = ax1.hist(dt, bins, color=colour)
    
    ax1.set_xlabel("\n" + xlabel, ha='center',
    va='center', fontsize=24)
    ax1.set_ylabel(ylabel + "\n", ha='center',
    va='center', fontsize=24)
    
    plt.savefig(out_fig)
    plt.close(f)
    high = 0
    popval = 0
    tot = 0.01
    for i in range(0, len(n)):
        if n[i] >= high:
            high = n[i]
            popval = b[i]
        tot += n[i]
    
    return (high, popval)

if __name__ == "__main__":
    histo("./../../lib/test scripts/logs/inp_only/log_hall_11 25 32 PV=16.csv", "./figsenshisto.png", r"$Interval, ms$", r"$Occurance$")
