# plots a most lovely figure showing how well the final filter choice works

import sys

sys.path.append('./../../lib')

from filter import filter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

def filterff(path_file, filter_method="butter", A=0.314, B=0.314):
    # load up some noisy data
    print "loading data"
    logf = open(path_file, "r")
    dat = logf.readlines()
    logf.close()
    
    # sort the loaded data into lists
    t = [0] * 0  # x, time
    s = [0] * 0  # y, speed
    start = 0.0  # start time (since epoch)
    st = [0] * 0 # specific time (time since run begun, seconds)
    
    print "sorting..."

    splt = dat[1].split(",", 5)
    t.append(float(splt[0]))
    s.append(float(splt[2]))
    start = t[0]
    st.append(0.0)

    for i in range(2, len(dat)):
        splt = dat[i].split(",", 5)
        t.append(float(splt[0]))
        s.append(float(splt[2]))
        st.append(t[i - 1] - start)
    
    print "sorted"
    print "applying filter"
    # Apply filter
    c = filter(t, s, method=filter_method)
    return st, s, c

def get_ft(x, y, f):
    # get spectra
    dt = x[-1] / len(x)
    # get frequency range (x)
    w = np.fft.fftfreq(len(x), d=dt)
    w = np.abs(w[:((len(x) / 2) + 1)])
    # get fourier transform of noisy signal (y1)
    ft = np.fft.rfft(y)
    ps_n = np.real(ft*np.conj(ft))*np.square(dt)
    # get fourier transform of filtered signal (y2)
    ft = np.fft.rfft(f)
    ps_f = np.real(ft*np.conj(ft))*np.square(dt)  
    return w, ps_n, ps_f

if __name__ == "__main__":
    # test script for testing
    # wiener averages too much and loses data
    # don't use spline - graphical method has little correlation to actual data
    # (tuned) butterworth seems to work well (A=2, nyf=0.05  

    method = "butter"

    # load up some noisy data
    # normal run (1)
    x1, y1, f1 = filterff("./../../lib/test scripts/logs/cur_read_get.csv", filter_method=method)
    # intermittent load
    x2, y2, f2 = filterff("./../../lib/test scripts/logs/intermittent_load.csv", filter_method=method)
    
    print "plotting"
    # Set up figure
    f = plt.figure(figsize=(16, 16))
    ax_tl = f.add_subplot(221)
    plt.title("$a)\ Steady\ Speed\ Increase$\n", fontsize=24)
    ax_tr = f.add_subplot(222)
    plt.title("$c)\ Frequency\ Spectra\ (Fourier\ Transform)$\n", fontsize=24)
    ax_b = f.add_subplot(212)
    plt.title("$b)\ Intermittent\ Load$", fontsize=24)
    
    # get spectra
    w, ps_n, ps_f = get_ft(x1, y1, f1)

    # Plot data and trendline
    ax_tl.plot(x1, y1, 'b', color=(0,0,1,0.2))
    ax_tl.plot(x1, f1, 'b')
    ax_tl.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax_tl.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)
    
    ps_offs = 0
    ax_tr.set_ylim([0, 500000])
    ax_tr.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
    ax_tr.plot(w[ps_offs:], ps_n[ps_offs:len(w)], 'b', color=(0,0,1,0.2))
    ax_tr.plot(w[ps_offs:], ps_f[ps_offs:len(w)], 'b')
    ax_tr.set_xlabel("\n $Frequency,\ Hz$", ha='center', va='center', fontsize=24)
    ax_tr.set_ylabel("", ha='center', va='center', fontsize=24)

    ax_b.plot(x2, y2, 'b', color=(0,0,1,0.2))
    ax_b.plot(x2, f2, 'b')
    ax_b.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
    ax_b.set_ylabel("$Speed,\ RPM$\n", ha='center', va='center', fontsize=24)

    #plt.title("$Filter\ Type:\ {0}$".format(method), fontsize=20)

    # Show plot
    print "saving plot"
    #plt.show()
    plt.savefig("./fig_filter_demons.png")
    plt.close(f)
