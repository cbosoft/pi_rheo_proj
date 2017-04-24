# plots a most lovely figure showing how well the final filter choice works

import sys

sys.path.append('./../../bin')

from filter import filter
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import scipy.fftpack
    
def fftnoise(f):
    f = np.array(f, dtype='complex')
    Np = (len(f) - 1) // 2
    phases = np.random.rand(Np) * 2 * np.pi
    phases = np.cos(phases) + 1j * np.sin(phases)
    f[1:Np+1] *= phases
    f[-1:-1-Np:-1] = np.conj(f[1:Np+1])
    return np.fft.ifft(f).real

def band_limited_noise(min_freq, max_freq, samples=1024, samplerate=1):
    freqs = np.abs(np.fft.fftfreq(samples, 1/samplerate))
    f = np.zeros(samples)
    idx = np.where(np.logical_and(freqs>=min_freq, freqs<=max_freq))[0]
    f[idx] = 1
    return fftnoise(f)

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
    
    N = len(x)
    T = (x[-1] - x[0]) / N
    
    yf = scipy.fftpack.fft(y)
    yf = 2.0/N * np.abs(yf[:N//2])
    ff = scipy.fftpack.fft(f)
    ff = 2.0/N * np.abs(ff[:N//2])
    xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
    
    ps_n = yf
    ps_f = ff
    w = xf
    #print ps_f
    return w, ps_n, ps_f

if __name__ == "__main__":
    # load up some noisy data
    datf = pd.read_csv("./../../logs/long_cal.csv")
    
    st = np.array(datf['t'])
    st = st - float(st[0])
    dr = np.array(datf['dr'])
    
    
    
    drf = filter(st, dr, method="butter", A=2, B=0.01)
    
    # add specific noise (10Hz)
    noise = band_limited_noise(0.1, 0.11, samples=len(dr))
    noisy = dr #+ (10000 * noise)
    
    # get fourier transform
    w, ps_n, ps_f = get_ft(st, dr, drf)
    
    # set up figure
    f = plt.figure(figsize=(8, 8))
    ax = f.add_subplot(111)
    
    # plot signal
    #ax.plot(st, dr)
    #ax.plot(st, noisy)
    ps_offs = 0
    ax.set_ylim([0, 0.1])
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
    ax.plot(w, ps_n, 'b', color=(0,0,1,0.2))
    ax.plot(w, ps_f, 'b')
    ax.set_xlabel("\n $Frequency,\ Hz$", ha='center', va='center', fontsize=24)
    ax.set_ylabel("", ha='center', va='center', fontsize=24)

    # save plot
    plt.grid(which='both', axis='both')
    plt.savefig("./fig_filt_demonstra.png")
    plt.close(f)
