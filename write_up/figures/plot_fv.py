import sys

sys.path.append("./../../bin")

from filter import filter

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import glob

import pandas as pd
from plothelp import fit_line, svf, cvf1, cvf2, vsvf



############ MOTOR COIL CURRENT CALIBRATION (MC3) ############

# Read data from empty run .csv
datmc3 = pd.read_csv("./../../logs/dual_hes_long100.csv")

st = np.array(datmc3['t'], np.float64)
st = st - st[0]

crmc3 = np.array(datmc3['cr'], np.float64)
cr2amc3 = np.array(datmc3['cr2a'], np.float64)
cr2bmc3 = np.array(datmc3['cr2b'], np.float64)
pv = np.array(datmc3['pv'], np.float64)

crmc3 = filter(st, crmc3, method="butter", A=2, B=0.001)
cr2amc3 = filter(st, cr2amc3, method="butter", A=2, B=0.001)
cr2bmc3 = filter(st, cr2bmc3, method="butter", A=2, B=0.001)

cu = (cvf1(crmc3) + cvf2(cr2amc3) + cvf2(cr2bmc3)) / 3
custd = [0] * len(cu)
for i in range(0, len(cu)):
    custd[i] = (max(cvf1(crmc3[i]), cvf2(cr2amc3[i]), cvf2(cr2bmc3[i])) - min(cvf1(crmc3[i]), cvf2(cr2amc3[i]), cvf2(cr2bmc3[i])))

sv = vsvf(pv)
    
# Chop off outlying data
start = 3000
stop = -1
skip = 2000

sv = sv[start:stop:skip]
cu = cu[start:stop:skip]
custd = custd[start:stop:skip]

fit, fiteqn, icoilcoeffs = fit_line(sv, cu, 1, x_name="V_{ms}", y_name="I_{coil}")

f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

ax.errorbar(sv, cu, yerr=custd, linestyle='None', marker='o', label="$Read\ data$")
ax.plot(sv, fit, label=fiteqn)

ax.set_xlabel("\n $V_{ms},\ Supply\ Voltage,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$I_{coil},\ Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)
plt.grid(which='both', axis='both')
plt.legend(loc=4)
plt.savefig("./fig_ico_cal.png")
plt.close(f)

def ico(vms):
    return icoilcoeffs[0] * vms + icoilcoeffs[1]


############ MOTOR EMF CURRENT AND STALL TORQUE CALIBRATION (MCST) ############

# Read data from pure glycerol load run .csv
datmcst = pd.read_csv("./../../logs/g1000v.csv")

stmcst = np.array(datmcst['t'], np.float64)
stmcst = stmcst - stmcst[0]

start2 = 35000
stop2 = -1
skip2 = 10000
crmcst = filter(st, np.array(datmcst['cr'], np.float64), method="butter", A=2, B=0.001)[start2:stop2:skip2]
cr2amcst = filter(st, np.array(datmcst['cr2a'], np.float64), method="butter", A=2, B=0.001)[start2:stop2:skip2]
cr2bmcst = filter(st, np.array(datmcst['cr2b'], np.float64), method="butter", A=2, B=0.001)[start2:stop2:skip2]
drmcst = filter(st, np.array(datmcst['dr'], np.float64), method="butter", A=2, B=0.001)[start2:stop2:skip2]
pvmcst = filter(st, np.array(datmcst['pv'], np.float64), method="butter", A=2, B=0.001)[start2:stop2:skip2]

cumcst = (cvf1(crmcst) + cvf2(cr2amcst) + cvf2(cr2bmcst)) / 3


# Geometry of the couette cell
roo = 0.044151 / 2.0  # outer cell outer radius in m
ro = 0.039111 / 2.0  # outer cell radius in m
ri = 0.01525  # inner cell radius in m

icxsa = np.pi * (ri ** 2)
ocxsa = np.pi * (ro ** 2)
dxsa = ocxsa - icxsa  # vol per height in m3/m
dxsa = dxsa * 1000 # l / m
dxsa = dxsa * 1000 # ml / m

fill_height = 15 / dxsa

# Calculate the required stall torque for these readings
mus    = [1.382] * len(cumcst)
sp_rpms = drmcst * 308.768 - 167.08
sp_rads = (sp_rpms * 2 * np.pi) / 60
sn_rpms = 5.13 * pvmcst + 15.275
gam_dot = (sp_rads * ri) / (ro - ri)
tau     = mus * gam_dot
svmcst  = (pvmcst * 0.066 + 2.278)
T       = tau * (2 * np.pi * ri * ri * fill_height) 
Ts      = T / (1.0 - (sp_rpms / sn_rpms))
icoil   = icoilcoeffs[0] * svmcst + icoilcoeffs[1]
imsmico = cumcst - icoil
ys = imsmico / Ts

custdcst = [0] * len(T)
for i in range(0, len(T)):
    custdcst[i] = (max((11.307 * cr2amcst[i] - 29.066), (11.307 * cr2bmcst[i] - 29.066), (16.573 * crmcst[i] - 29.778)) - min((11.307 * cr2amcst[i] - 29.066), (11.307 * cr2bmcst[i] - 29.066), (16.573 * crmcst[i] - 29.778)))
    custdcst[i] = custdcst[i] / np.average(Ts)

fit, fiteqn, emftscoeffs = fit_line(svmcst, ys, 1, x_name="V_{ms}", y_name="I_{emf}/T_S")

f = plt.figure(figsize=(8,8))
ax = f.add_subplot(111)

ax.errorbar(svmcst, ys, yerr=custdcst, linestyle='None', marker='o', label="$Read\ Data$")
ax.plot(svmcst, fit, 'g', label=fiteqn)

ax.set_xlabel("\n $V_{ms},\ Supply\ Voltage,\ V$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$I_{emf}/T_S,\ A/N\,m$\n", ha='center', va='center', fontsize=24)
ax.set_ylim([0, max(ys)])
plt.grid(which='both', axis='both')
plt.legend()
plt.savefig("./fig_emf_ts_cal.png")
plt.close(f)

def emfts(vms):
    return emftscoeffs[0] * vms + emftscoeffs[1]

############ VISCOSITY CALCULATION USING ABOVE CORRELATIONS ############

def getmu(filename, start=0, stop=-1, skip=1):
    dat = pd.read_csv(filename)
    st = np.array(dat['t'], np.float64)
    st = st - st[0]
    dr = np.array(dat['dr'], np.float64)
    cr = np.array(dat['cr'], np.float64)
    cra = np.array(dat['cr2a'], np.float64)
    crb = np.array(dat['cr2b'], np.float64)
    pv = np.array(dat['pv'], np.float64)

    cu1 = cvf1(cr)
    cu2a = cvf2(cra)
    cu2b = cvf2(crb)

    cu = (cu1 + cu2a + cu2b) / 3


    cu = filter(st, cu, method="butter", A=2, B=0.0001)
    dr = filter(st, dr, method="butter", A=2, B=0.0001)

    sv = vsvf(pv)

    T = (cu - ico(sv)) / (emfts(sv))
    tau = T / (2 * np.pi * ri * ri * fill_height) 

    sp_rpms = svf(dr)
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    gam_dot = (sp_rads * ri) / (ro - ri)

    mu = tau / gam_dot

    # Chop off unwanted data
    st = st[start:stop:skip]
    mu = mu[start:stop:skip]
    gam_dot = gam_dot[start:stop:skip]
    tau = tau[start:stop:skip]
    return st, gam_dot, mu, tau

st = [0] * 5
gam_dot = [0] * 5
mu = [0] * 5
tau = [0] * 5

st[0], gam_dot[0], mu[0], tau[0] = getmu("./../../logs/g1000v.csv")
st[1], gam_dot[1], mu[1], tau[1] = getmu("./../../logs/g9873c.csv", start=100000)
st[2], gam_dot[2], mu[2], tau[2] = getmu("./../../logs/g9623c.csv", start=30000)
st[3], gam_dot[3], mu[3], tau[3] = getmu("./../../logs/g9375c.csv", start=30000)
st[4], gam_dot[4], mu[4], tau[4] = getmu("./../../logs/g8887c.csv", start=30000)

f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)

x = gam_dot
y = mu

ax.errorbar(np.average(x[1]), np.average(y[1]), xerr=np.std(x[1]), yerr=np.std(y[1]), marker='o', linestyle='None')
ax.errorbar(np.average(x[2]), np.average(y[2]), xerr=np.std(x[2]), yerr=np.std(y[2]), marker='o', linestyle='None')
ax.errorbar(np.average(x[3]), np.average(y[3]), xerr=np.std(x[3]), yerr=np.std(y[3]), marker='o', linestyle='None')
ax.errorbar(np.average(x[4]), np.average(y[4]), xerr=np.std(x[4]), yerr=np.std(y[4]), marker='o', linestyle='None')

ax.set_xlabel("\n" + r"$\dot\gamma,\ Strain\ Rate,\ \rm s^{-1}$", ha='center', va='center', fontsize=24)
#ax.set_ylabel(r"$\mu,\ Viscosity\,\ \rm Pa\,s$" + "\n", ha='center', va='center', fontsize=24)
ax.set_ylabel(r"$\tau,\ Shear\ Stress\,\ \rm Pa$" + "\n", ha='center', va='center', fontsize=24)
#ax.set_ylim([-100, 100])
plt.grid(which='both', axis='both')
#plt.legend()
plt.savefig("./fig_mu_res.png")
















sys.exit()

































def fitf(x, a, b):
    return a * x[0] + b + 0.0156 * x[1]

def fit2f(x, a, b):
    return a * (x[0]) + b

# DISABLE THIS SCRIPT!!!!!
sys.exit()

    
# Geometry of the couette cell
roo = 0.044151 / 2.0  # outer cell outer radius in m
ro = 0.039111 / 2.0  # outer cell radius in m
ri = 0.01525  # inner cell radius in m

icxsa = np.pi * (ri ** 2)
ocxsa = np.pi * (ro ** 2)
dxsa = ocxsa - icxsa  # vol per height in m3/m
dxsa = dxsa * 1000 # l / m
dxsa = dxsa * 1000 # ml / m

fill_height = 15 / dxsa

# Reads the data
datf = pd.read_csv("./../../logs/g9873c.csv")

stg     = datf['t']
stg     = stg - stg[0]
dr      = datf['dr']
cr      = datf['cr']
cr2a    = datf['cr2a']
cr2b    = datf['cr2b']
pv      = datf['pv']

# Filter noise from data
dr = filter(stg, dr, method="butter", A=2, B=0.0001)
cr = filter(stg, cr, method="butter", A=2, B=0.0001)
cr2a = filter(stg, cr2a, method="butter", A=2, B=0.0001)
cr2b = filter(stg, cr2b, method="butter", A=2, B=0.0001)

# Chop off unwanted data
start   = 20000
stop    = -1 * (int(len(cr) * 1) - 25000)
skip    = 1000
stg     = stg[start:stop:skip]
dr      = dr[start:stop:skip]
cr      = cr[start:stop:skip]
cr2a    = cr2a[start:stop:skip]
cr2b    = cr2b[start:stop:skip]
pv      = pv[start:stop:skip]

# Calculate the required stall torque for these readings
musg    = [1.129] * len(cr)
sp_rpms = dr * 316.451 - 163.091
sp_rads = (sp_rpms * 2 * np.pi) / 60
sn_rpms = 5.13 * pv + 15.275
gam_dot = (sp_rads * ri) / (ro - ri)
tau     = musg * gam_dot
T       = tau * (2 * np.pi * ri * ri * fill_height) 

Ts      = T / (1.0 - (sp_rpms / sn_rpms))
cu      = 16.573 * cr - 29.778
cu2a    = 11.307 * cr2a - 29.066
cu2b    = 11.307 * cr2b - 29.066
cub     = 0.00229473 * pv + 0.48960784
cu      = (cu + cu2a + cu2b) / 3
vo      = 0.0636 * pv + 2.423

# Relate the stall torque to the current supply
eff, __ =  curve_fit(fit2f, [(cu - cub)], T)

# Calculate the viscosity using the read data and the fit
Tg_fc       = eff[0] * ((cu - cub)*vo) + eff[1]
taug_fc     = Tg_fc / (2 * np.pi * ri * ri * fill_height)
mug_fc = taug_fc / gam_dot

f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)
ax.errorbar((cu - cub), T, 
    xerr=(0.05 * np.array(cu)), marker='o', linestyle='None', label="$Required\ Torque$")
ax.plot((cu-cub), ((cu - cub) * eff[0] + eff[1]), label="$T\ =\ {:.3E} * \Delta I_{} + {:.3E}$".format(eff[0], "{ms}", eff[1]))

ax.set_xlabel("\n $\Delta Current,\ A$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Torque,\ Nm$\n", ha='center', va='center', fontsize=24)
plt.legend(loc=4)
plt.grid(which='both', axis='both')
plt.savefig("./fig_t_cal.png")

def check(filename, viscosity, fillvol):
    ########### Check the calibration using the water run
    # Reads the data

    # Geometry of the couette cell

    roo = 0.044151 / 2.0  # outer cell outer radius in m
    ro = 0.039111 / 2.0  # outer cell radius in m
    ri = 0.01525  # inner cell radius in m

    icxsa = np.pi * (ri ** 2)
    ocxsa = np.pi * (ro ** 2)
    dxsa = ocxsa - icxsa  # vol per height in m3/m
    dxsa = dxsa * 1000 # l / m
    dxsa = dxsa * 1000 # ml / m

    fill_height = fillvol / dxsa

    datf = pd.read_csv(filename)

    stw     = datf['t']
    stw     = stw - stw[0]
    dr      = datf['dr']
    cr      = datf['cr']
    cr2a    = datf['cr2a']
    cr2b    = datf['cr2b']
    pv      = datf['pv']

    # Filter noise from data
    dr      = filter(stw, dr, method="butter", A=2, B=0.001)
    cr      = filter(stw, cr, method="butter", A=2, B=0.001)
    cr2a    = filter(stw, cr2a, method="butter", A=2, B=0.001)
    cr2b    = filter(stw, cr2b, method="butter", A=2, B=0.001)

    # Calculate viscosity
    musw    = [viscosity] * len(cr)
    cu      = 16.573 * cr - 29.778
    cu2a    = 11.307 * cr2a - 29.066
    cu2b    = 11.307 * cr2b - 29.066
    cu      = np.array((cu + cu2a + cu2b) / 3)
    cub     = 0.00229473 * pv + 0.48960784
    sp_rpms = dr * 316.451 - 163.091
    sp_rads = (sp_rpms * 2 * np.pi) / 60
    sn_rpms = 5.13 * pv + 15.275
    vo      = 0.0636 * pv + 2.423

    #T calibration
    gam_dotw    = (sp_rads * ri) / (ro - ri)
    #Tw_fc       = eff[0] * (cu - cub) + eff[1]
    Tw_fc       = eff[0] * ((cu - cub) *vo) + eff[1]
    tauw_fc     = Tw_fc / (2 * np.pi * ri * ri * fill_height) 
    muw_fc = tauw_fc / gam_dotw
    return stw, muw_fc, musw

st9873, mufc9873, mus9873 = check("./../../logs/g9873c.csv", 1.129, 15)
st9623, mufc9623, mus9623 = check("./../../logs/g9623c.csv", 0.9061, 15)
st9375, mufc9375, mus9375 = check("./../../logs/g9375c.csv", 0.6102, 15)
st8887, mufc8887, mus8887 = check("./../../logs/g8887c.csv", 0.4005, 15)

# Plot
f = plt.figure(figsize=(8, 8))
ax = f.add_subplot(111)
start = 20000
stop = -1 * (len(st9873) - 115000)
skip = 1000
ax.plot(stg, musg, 'b')
ax.plot(stg, mug_fc, 'bx')

ax.plot(st9375[start:stop:skip], mus9375[start:stop:skip], 'g')
ax.plot(st9375[start:stop:skip], mufc9375[start:stop:skip], 'g^')

ax.plot(st9623[start:stop:skip], mus9623[start:stop:skip], 'r')
ax.plot(st9623[start:stop:skip], mufc9623[start:stop:skip], 'r^')
ax.set_yscale('log')
ax.set_xlabel("\n $Time,\ s$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Viscosity,\ Pa.s$\n", ha='center', va='center', fontsize=24)
plt.grid(which='both', axis='both')
plt.savefig("./fig_t_check.png")
