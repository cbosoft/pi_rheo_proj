#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

from lmfit.models import ExpressionModel, ExponentialGaussianModel
from lmfit import Parameter

from control import tf_pi_controller as pitf

pic = pitf((0.2, 0.15))

Ys, Es, Us, Ts = pic.do_sim(0.072, 4.76)

gmod = ExpressionModel("a*(sin(3.14159 * omega * x) * exp(-tau * x)) + offset")
result = gmod.fit(Ys, a=10, omega=1, x=Ts, tau=Parameter('tau', 1, vary=True), offset=Parameter('offset', 200, vary=False))
#gmod= ExpressionModel("(H * exp(-t * x)) + voff")
#result = gmod.fit(y, H=250, t=0.2, x=x, voff=100)

#modl = ExponentialGaussianModel()
#result = modl.fit(y, amplitude=175, center=20, sigma=0.5, gamma=0.25, x=x)
print(result.fit_report())

plt.plot(Ts, Ys, 'b')
plt.plot(Ts, result.best_fit, 'r-')
plt.savefig("./test.png")
