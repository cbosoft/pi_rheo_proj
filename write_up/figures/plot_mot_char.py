#
# Calculates the torque  and efficiency from the read data
#

import sys

sys.path.append('./../../bin')

from filter import filter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick



if False:

    print "loading geometry"
    logf = open("./../../logs/cell_geom.csv", "r")
    dat = logf.readlines()
    logf.close()
    
    ocod = 0
    ocid = 0
    och = 0
    icd = 0
    ich = 0
    
    for i in range(0, len(dat)):
        splt = dat[i].split(",")
        if splt[0] == "ocod": ocod = float(splt[10])
        if splt[0] == "ocid": ocid = float(splt[10])
        if splt[0] == "och": och = float(splt[10])
        if splt[0] == "icd": icd = float(splt[10])
        if splt[0] == "ich": ich = float(splt[10])
    
    r = icd / 2
    radsperrpm = (1.0 / (60.0 * 2 * np.pi))
    
    print "loading data"
    logf = open("./../../logs/motor_charact_main.csv", "r")
    dat = logf.readlines()
    logf.close()
    
    # sort the loaded data into lists

    # read data
    pv = [0] * 0  # pot value
    we = [0] * 0  # weight, grams
    cr = [0] * 0  # HES reading, V
    dr = [0] * 0  # Dynamo reading, V

    # calculated data
    sv = [0] * 0  # Supply voltage, V
    fo = [0] * 0  # Force, N
    cu = [0] * 0  # Current supply, A
    sp = [0] * 0  # Speed, rad/s
    to = [0] * 0  # Torque, Nm
    pe = [0] * 0  # Electrical power, W
    pm = [0] * 0  # Mechanical (shaft) power, W
    ef = [0] * 0  # Efficiency

    for i in range(1, len(dat)):

        splt = dat[i].split(",")
        pv.append(float(splt[0]))
        we.append(float(splt[1]))
        cr.append(float(splt[2]))
        dr.append(float(splt[3]))

        sv.append((0.066 * pv[-1]) + 2.278)
        fo.append(9.80665 * we[-1] * 0.001)
        cu.append((3.58 * cr[-1]) - 7.784)
        sp.append(radsperrpm * ((317.666 * dr[-1]) - 146.947))
        to.append(fo[-1] * r)
        pe.append(cu[-1] * sv[-1])
        pm.append(to[-1] * sp[-1])
        ef.append(pm[-1] / pe[-1])
    
    print "plotting"
    # Set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
#    plt.title("$a)\ Efficiency\ vs\ Torque$\n", fontsize=24)

    # Plot data
    #ax.plot(to, ef, 'bx')
    #ax.set_xlabel("\n $Torque,\ Nm$", ha='center', va='center', fontsize=24)
    #ax.set_ylabel("$Efficiency$\n", ha='center', va='center', fontsize=24)

    # Plot data
    ax.plot(pv, sv, 'bx')
#    ax.set_xlabel("\n $Torque,\ Nm$", ha='center', va='center', fontsize=24)
#    ax.set_ylabel("$Efficiency$\n", ha='center', va='center', fontsize=24)

    # Show plot
    print "saving plot"
    #plt.show()
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_mot_charac.png")
    plt.close(f)
