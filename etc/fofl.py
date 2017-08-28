from sys import argv
from sys import path

import matplotlib.ticker as tck
import matplotlib.pyplot as plt
import numpy as np
import numpy.fft as ft

path.append("./../bin/")

import plothelp as ph

t, st, dr, cr, cr2a, cr2b, pv, T, Vpz, gamma_dot, tau, tag = ph.read_logf(argv[1])

ftt_dr = ft.fft(dr)
freq = ft.fftfreq(len(dr), st[1])

#plt.plot(st, ftt_dr)
#plt.show()

plt.plot(freq / np.pi, ftt_dr) #np.angle(ftt_dr))

ax = plt.gca()
ax.xaxis.set_major_formatter(tck.FormatStrFormatter('%g $\pi\ rads^{-1}$'))
ax.xaxis.set_major_locator(tck.MultipleLocator(base=1.0))

plt.show()
