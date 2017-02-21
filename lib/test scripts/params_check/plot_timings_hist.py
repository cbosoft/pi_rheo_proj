#
# For each file, get range of values (ideal is 0) and plot range vs number
#
import matplotlib.pyplot as plt
import numpy as np
from glob import glob

def min_max(log_path):
    #Read logfile
    datf = open(log_path, "r")
    datl = datf.readlines()
    datf.close()
    
    # Create lists
    s = [0] * (len(datl))  # Time

    # Split data into lists for easy use
    for i in range(1, len(datl)):
        splt = datl[i].split(",", 5)
        try:
            s[i] = float(splt[2])
        except:
            s[i] = 0.0

    high = 0.0
    low = 100000.0

    for i in range(0, len(s)):
        if s[i] > high:
            high = s[i]
        if s[i] < low:
            low = s[i]
    
    return (high, low)

if __name__ == "__main__":
    rnges = [0.0] * 0
    for p in sorted(glob(r"./log_?? *.csv")):
        (h, l) = min_max(p)
        rnges.append((h - l))


    # Plot (meta) Data
    f = plt.figure(figsize=(10, 10))
    ax1 = f.add_subplot(111)

    clrs = ["b", "g", "r", "c", "m", "y", "k", "0.75", "0.5", "0.25", "#eeAAff"]
    mkrs = [".", "o", "v", "8", "*", "<", "x", "|", "D", "H", "+"]
    lab = [0]*0
    for i in range (0, 11):
        lab.append("$SPAN = {0:.3f}$".format(float(i) * 0.1))

    for ot in range(0, 11):
        ax1.scatter([0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.2], rnges[((ot * 11) + 3):((ot * 11) + 11)], color=clrs[(ot)], marker=mkrs[ot], label = lab[ot])

    ax1.set_xlabel("$Inverse\ Poll\ Rate,\ ms$", ha='center',
    va='center', fontsize=16)

    ax1.set_ylabel("$Speed\ Range,\ RPM$", ha='center',
    va='center', fontsize=16)
    plt.legend(loc=3)
    plt.savefig("meta_plot_light.png")
