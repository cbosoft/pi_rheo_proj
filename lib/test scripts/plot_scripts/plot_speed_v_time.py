import matplotlib.pyplot as plt
import numpy as np
from glob import glob

# Read csv

logs = sorted(glob("./../logs/*.csv"))  # gets a list of all csvs in directory

for l in range(0, len(logs)):
    print "opening log {0}".format(logs[l])
    datf = open(logs[l], "r")  # opens the latest one
    datl = datf.readlines()
    datf.close()

    # Create lists for sorting

    speed = [0] * 0
    t = [0] * 0
    st = [0] * 0
    pv = [0] * 0

    splt = datl[1].split(",", 5)
    tz = float(splt[0])
    
    for i in range(2, len(datl) - 2):
        splt = datl[i].split(",", 5)
        t.append(float(splt[0]))
        speed.append(float(splt[2]))
        st.append(float(splt[0]) - tz)
        pv.append(int(splt[4]))

    # Speed v Time  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
    # Set up figure
    f = plt.figure(figsize=(7, 7))
    ax = f.add_subplot(111)

    # Calculate trendline
    z = np.polyfit(st, speed, 1)
    tl = np.poly1d(z)

    # Plot data and trendline
    ax.plot(st, speed, 'o', label="$Recorded\ Speed$")
    ax.plot(st, tl(st), 'r--', label="$Trendline, SPD = {0:.3f}t + {1:.3f}$".format(z[0], z[1]))

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    # Show Legend
    plt.legend(loc=3)

    # Show Title
    plt.title(logs[l])

    # Show plot
    print "saving plot: {0}".format(l)
    plt.savefig("./figspeedvt{0}.png".format(l))
    plt.close(f)

    # Speed v Val  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #
    # Set up figure
    f = plt.figure(figsize=(7, 7))
    ax = f.add_subplot(111)

    # Calculate trendline
    z = np.polyfit(pv, speed, 1)
    tl = np.poly1d(z)

    # Plot data and trendline
    ax.plot(pv, speed, 'o', label="$Recorded\ Speed$")
    ax.plot(pv, tl(pv), 'r--', label="$Trendline, SPD = {0:.3f}PV + {1:.3f}$".format(z[0], z[1]))

    ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    # Show Legend
    plt.legend(loc=3)

    # Show Title
    plt.title(logs[l])

    # Show plot
    print "saving plot: {0}".format(l)
    plt.savefig("./figspeedvv{0}.png".format(l))
    plt.close(f)

