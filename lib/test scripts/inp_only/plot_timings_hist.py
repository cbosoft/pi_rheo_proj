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
    f = plt.figure(figsize=(10, 7.5))
    ax1 = f.add_subplot(111)

    # Bins might need tweaking between datasets
    bins = np.linspace(0, 100, 100)

    (n, b, patches) = ax1.hist(dt, bins, color=colour)
    
    ax1.set_xlabel(xlabel, ha='center',
    va='center', fontsize=12)
    ax1.set_ylabel(ylabel, ha='center',
    va='center', fontsize=12)
    
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
    fracl = [0.0] * 0
    maxl = [0.0] * 0
    logno = [0.0] * 0
    for p in sorted(glob(r"./log_hall_*.csv")):
        (pop, popval) = histo(p, p + ".png", r"$Interval, ms$", r"$Occurance$")
        fracl.append(pop)
        maxl.append(popval)
        # logno.append(float(p[24:-4]))
    
    # Plot (meta) Data
    f = plt.figure(figsize=(10, 10))
    ax1 = f.add_subplot(111)
    #ax1.plot(logno, fracl)
    ax1.scatter(range(0, len(maxl)), maxl, color="red")
    #ax1.plot([logno[0], logno[0] + len(logno) - 1], [0.1, 0.1], color = "red")
    ax1.set_xlabel("$File$", ha='center',
    va='center', fontsize=16)
    ax1.set_ylabel("$Most Frequent Interval Time$", ha='center',
    va='center', fontsize=16)
    
    plt.savefig("meta_plot_light.png")
