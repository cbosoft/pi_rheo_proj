from glob import glob
from rheometer import rheometer as rh
import matplotlib.pyplot as plt

r = rh()
f = plt.figure()
ax = f.add_subplot(111)

for g in glob("./../logs/rheometry_test_*_*.csv"):

    mu = r.calc_visc(g, 15)

    ax.plot(mu, label=g)
ax.legend()
plt.show()
