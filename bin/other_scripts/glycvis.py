import numpy as np

def get_mixture_viscosity(T, Cm):
    a = 0.705 - 0.0017 * T
    b = (4.9 + 0.036 * T)
    alp = 1 - Cm + (a * b * Cm * (1 - Cm))/(a * Cm + b * (1 - Cm))
    muw = 1.79 * np.exp(((-1230 - T) * T) / (36100 + 360 * T))
    mug = 12100 * np.exp(((-1233 + T) * T)/(9900 + 70 * T))
    #print "| a: {:.3f} \t\t\t| b: {:.3f} \t\t\t| alp: {:.3f}\t|".format(a, b, alp)
    #print "| muw: {:.3f} \t\t\t| mug: {:.3f} \t\t\t| alp: {:.3f}\t|".format(muw, mug, alp)
    mum = (muw ** alp) * (mug ** (1- alp))
    return mum

def get_mixture_composition(T, mum):
    a = 0.705 - 0.0017 * T
    b = (4.9 + 0.036 * T)
    muw = 1.79 * np.exp(((-1230 - T) * T) / (36100 + 360 * T))
    mug = 12100 * np.exp(((-1233 + T) * T)/(9900 + 70 * T))
    alp = (np.log(mum / mug)) / (np.log(muw / mug))
    ba = a * (1 + b) - b
    bb = (a - b) * alp + (2 * b) - a - a * b
    bc = b * (alp - 1)
    #print "| a: {:.3f} \t\t\t| b: {:.3f} \t\t\t| alp: {:.3f}\t|".format(a, b, alp)
    #print "| A: {:.3f} \t\t\t| B: {:.3f} \t\t\t| C: {:.3f} \t|".format(ba, bb, bc)
    print "| muw: {} \t\t\t| mug: {} \t\t\t| alp: {}\t|".format(muw, mug, alp)
    Cmp = ((-1 * bb) + ((bb**2) - 4 * ba * bc) ** 0.5) / (2 * ba)
    Cmm = ((-1 * bb) - ((bb**2) - 4 * ba * bc) ** 0.5) / (2 * ba)
    Cm = Cmp
    for i in range(0, len(Cm)):
        if Cm[i] < 0:# or Cm[i] > 1:
            Cm[i] = Cmm[i]
            if Cm[i] < 0:# or Cm[i] > 1:
                Cm[i] = np.nan
    return mum, Cm
    

if __name__ == "__main__":
    mus = np.linspace(0, 1000, 11)
    __, cs = get_mixture_composition(20, mus)
    for i in range(0, len(mus)):
        print "Mu: {:.3f}\t Cm: {:.3f}".format(mus[i], cs[i])
