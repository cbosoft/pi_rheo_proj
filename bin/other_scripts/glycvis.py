#
# Calculates the viscosity of a mixture of glycerol (glycerine) and water
#
# Also calculates the composition of such given a viscosity

import numpy as np

def get_mixture_viscosity(T, Cm):

    a       = 0.705 - 0.0017 * T
    b       = (4.9 + 0.036 * T)
    T       = float(T)
    alp     = 1 - Cm + (a * b * Cm * (1 - Cm))/(a * Cm + b * (1 - Cm))
    muw     = 1.79 * np.exp( ( ( (-1230.0 * T) - (T ** 2) ) ) / (36100.0 + (360.0 * T)))
    mug     = 12100.0 * np.exp(((-1233.0 + T) * T)/(9900.0 + 70.0 * T))
    mum     = (muw ** alp) * (mug ** (1- alp)) * 0.001
    
    return mum

def get_mixture_composition(T, mum):

    a       = 0.705 - 0.0017 * T
    b       = (4.9 + 0.036 * T)
    T       = float(T)
    muw     = 1.79 * np.exp( ( ( (-1230.0 * T) - (T ** 2) ) ) / (36100.0 + (360.0 * T)))
    mug     = 12100.0 * np.exp(((-1233.0 + T) * T)/(9900.0 + 70.0 * T))
    alp     = (np.log(mum / mug)) / (np.log(muw / mug))
    ba      = a * (1 + b) - b
    bb      = (a - b) * alp + (2 * b) - a - a * b
    bc      = b * (alp - 1)
    Cmp     = ((-1 * bb) + ((bb**2) - 4 * ba * bc) ** 0.5) / (2 * ba)
    Cmm     = ((-1 * bb) - ((bb**2) - 4 * ba * bc) ** 0.5) / (2 * ba)
    Cm      = Cmp
    
    for i in range(0, len(Cm)):
        if Cm[i] < 0:
            Cm[i] = Cmm[i]
            if Cm[i] < 0:
                Cm[i] = np.nan

    rhow    = 1000.0 * (1.0 - abs((T - 4.0) / 622.0)**1.7)
    rhog    = 1277.0 - 0.654 * T
    print "{} {}".format(rhow, rhog)
    Vf      = (1.0 / ((1.0 / Cm) - 1.0)) * (rhow / rhog)
    V2f     = 1.0 / ((1.0 / Vf) + 1.0)
    
    return Cm, Vf, V2f

def get_strain(spd):
    return spd * 2 * np.pi * 0.015 / ((0.0195 - 0.015) * 60)
    

if __name__ == "__main__":
    mus = np.linspace(1.005, 1141, 5)
    mf, vf, vof = get_mixture_composition(20, mus)
    print mf[-1]
    mixvol = 20
    print "\n\t\t{}ml mixture\n".format(mixvol)
    print " Viscosity \t ml glycerol \t ml glycerol \t ml water"
    print " in cP  \t per ml water \t \n"           #per ml mix \t per ml mix\n"
    for i in range(0, len(mus)):
        print " {:.3f}   \t {:.3f}  \t {:.3f}   \t {:.3f}".format(mus[i], mf[i], vof[i] * mixvol, (1 - vof[i]) * mixvol)

    oms = get_mixture_viscosity(20, mf)
    print ""
    for i in range(0, len(oms)):
        print "Mu: {:.3f}\t Cm: {:.3f}".format(oms[i], mf[i])
