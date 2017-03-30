#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

from lmfit.models import ExpressionModel
from lmfit import Parameter

from control import PIDcontroller

pid = PIDcontroller(KP=0.1, KI=0.095, KD=0.0)
#pid.loud = True
#pid.tune(0.072, 4.76, steps=10, pmx=(0.01, 0.1),imx=(0.01, 0.01), dmx=(0.0, 0.0))

#x, y = pid.do_sim(0.072, 4.76, horiz_return=False, length=20, manual_sample_time=0.1)
x, y = pid.do_sim(1, 1, horiz_return=False, length=100, manual_sample_time=0.1)

#gmod = ExpressionModel("a*(sin(3.14159 * omega * x) * exp(-tau * x)) + offset")
#result = gmod.fit(y, a=10, omega=-1, x=x, tau=Parameter('tau', 0.2, vary=False), offset=0.04726)
gmod= ExpressionModel("(H * exp(-t * x)) + voff")
result = gmod.fit(y, H=250, t=0.2, x=x, voff=100)

print(result.fit_report())

plt.plot(x, y, 'bo')
plt.plot(x, result.best_fit, 'r-')
plt.savefig("./test.png")
