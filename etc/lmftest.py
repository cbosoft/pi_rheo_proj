from scipy.optimize import leastsq
import numpy as np
import matplotlib.pyplot as plt

def residual(vars, x, data):
    amp = vars[0]
    phaseshift = vars[1]
    freq = vars[2]
    decay = vars[3]

    model = amp * np.sin(x * freq  + phaseshift) * np.exp(-x*x*decay)

    return (data-model)

vars = [10.0, 0.2, 3.0, 0.007]

x = range(0, 100)
x = np.array(x, np.float64)
x = x * 0.01 * np.pi * 2
data = np.cos(x)

out = leastsq(residual, vars, args=(x, data))

amp = out[0][0]
phase = out[0][1]
freq = out[0][2]
decay = out[0][3]

print("Result:")
print("\tamplitude:\t{}".format(amp))
print("\tphase:    \t{}".format(phase))
print("\tfrequency:\t{}".format(freq))
print("\tdecay:    \t{}".format(decay))

model = amp * np.sin(x * freq  + phase) * np.exp(-x*x*decay)

f = plt.figure()
ax = f.add_subplot(111)
ax.plot(x, model)
ax.plot(x, data, "x")

if (np.log10(abs(decay)) > -5): 
    plt.title("Not stable sinusoid")
    print("Not stable sinusoid")
else:
    plt.title("Fine!")
    print("Fine!")

plt.show()