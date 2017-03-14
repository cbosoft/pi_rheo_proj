# simple script calculates/stores the uncertainties in readings etc
def gru(readings, smallest_increment):
    sum = 0.0
    
    for i in range(0, len(readings)):
        sum += readings[i]
        
    av = float(sum) / len(readings)
    
    du = [0.0] * 3
    du[0] = float(av) - float(sorted(readings)[0])
    du[1] = float(sorted(readings)[-1]) - float(av)
    du[2] = float(smallest_increment) / 2.0
    
    return sorted(du)[-1]


# couette cell geometry

ocod = [0.044, 0.044]               # outer cylinder outer diameter, m
ocodu = gru(ocod, 0.000001)         # uncertainty in ^

ocid = [0.04, 0.04]                 # outer cylinder inner diameter, m
ocidu = gru(ocid, 0.000001)         # uncertainty in ^

icd = [0.03015]                     # inner cylinder diameter, m
icdu = gru(icd, 0.000001)           # uncertainty in ^

# readings...

# 