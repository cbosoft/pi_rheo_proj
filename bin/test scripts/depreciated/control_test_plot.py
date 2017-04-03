import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import sys
sys.path.append("./..")
from filter import filter

files = sorted(glob("./control_test_log/0.1_0.01.csv"))
for i in range(0, len(files)):
    # Read csv
    fil = files[i]
    datf = open(fil, "r")
    datl = datf.readlines()
    datf.close()

    # Create lists for sorting

    ti = [0] * 0  # time
    dr = [0] * 0  # dynamo reading
    fdr = [0] * 0  # filtered dynamo reading (live)
    dpv = [0] * 0  # delta pv (dca)
    nca = [0] * 0  # control action
    st = [0] * 0

    for i in range(1, len(datl)):
        splt = datl[i].split(",")
        ti.append(float(splt[0]))
        dr.append(float(splt[1]))
        fdr.append(float(splt[2]))
        dpv.append(float(splt[3]))
        nca.append(float(splt[4]))

        st.append(ti[-1] - ti[0])

    # Set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    plt.title(fil)

    drf = filter(st, dr, method="butter", A=2, B=0.008)

    dr = np.array(dr)
    fdr = np.array(fdr)
    drf = np.array(drf)
    # Plot data
    #ax.plot(st, (dr * 316.415) - 163.091, '-', color=(0,0,1,0.25))
    ax.plot(st, (fdr * 316.415) - 163.091, '-', color=(0,0,1,0.5))
    #ax.plot(st, (drf * 316.415) - 163.091, 'b-')
    #a2x = ax.twinx()
    #plt.axhline(y=36, color='green')
    #a2x.plot(st, nca, 'g-')
    #ax.set_xlabel("\n $Current\ Supply,\ A$", ha='center', va='center', fontsize=24)
    #ax.set_ylabel("$Stall\ Torque,\ Nm$\n", ha='center', va='center', fontsize=24)

    # Show Legend
    #plt.legend(loc=1)

    # Show plot
    plt.grid(which='both', axis='both')
    plt.savefig("./contr_test.png")
    plt.close(f)
