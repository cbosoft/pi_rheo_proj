from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

# Create Data
cutoff = 0.08  # in radial frequency, rad/s
b, a = signal.butter(4, cutoff, 'low', analog=True)
w, h = signal.freqs(b, a)

x = np.divide(w, 2 * np.pi)
y = 20 * np.log10(abs(h))

# Set up figure
f = plt.figure(figsize=(7, 7))
ax = f.add_subplot(111)
plt.title("$4^{th}\ Order\ Butterworth\ Function\ Response$")
# Plot data and trendline
ax.plot(x, y)
plt.xscale('log')
plt.margins(0, 0.1)
plt.grid(which='both', axis='both')
#ax.set_xlabel("\n $Frequency,\ rads^{-1}$", ha='center', va='center', fontsize=24)
ax.set_xlabel("\n $Frequency,\ Hz$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Frequency\ Response$\n", ha='center', va='center', fontsize=24)

plt.axvline(cutoff / (2 * np.pi), color='green') # cutoff frequency

# Show plot
plt.savefig("./fig_butter.png")
