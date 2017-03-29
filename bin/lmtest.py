#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

from lmfit.models import ExpressionModel
from lmfit import Parameter

from control import PIDcontroller

pid = PIDcontroller(KP=0.09, KI=0.01, KD=0.0)
pid.loud = True
pid.tune(0.072, 4.76, steps=10, pmx=(0.0, 0.1),imx=(0.0, 0.1), dmx=(0.0, 0.0))

x, y = pid.do_sim(0.072, 4.76, horiz_return=False, length=20, manual_sample_time=0.1)

gmod = ExpressionModel("a*(sin(3.14159 * omega * x) * exp((-x) / tau)) + offset")

result = gmod.fit(y, a=0.5, omega=0.1, x=x, tau=0.1, offset=0.05)

print(result.fit_report())

plt.plot(x, y, 'bo')
plt.plot(x, result.best_fit, 'r-')
plt.show()