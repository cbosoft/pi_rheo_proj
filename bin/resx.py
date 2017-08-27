'''
Provides methods for easily reading and using calibration and geometry data from file.

Provides run-time access to the information stored in the /etc/data.xml file, including access 
to calibrations and the geometry of the cylinders.

Also has a few functions that allow the easy use of the calibrations ("get_supply_voltage(pv)" 
for example)

Author: Chris Boyle (christopher.boyle.101@strath.ac.uk)
'''

# 3rd Party
import xml.etree.ElementTree as ET
import numpy as np
from math import pi

# read the xml file
root = ET.parse('./../etc/data.xml').getroot()

def parse_root(name, type):
    global root
    for child in root:
        # can be geometry or calibration...
        if child.tag == type and type == "geometry":
            if child.attrib["name"] == name:
                return float(child[0].text)
        elif child.tag == type and type == "calibration":
            if child.attrib["name"] == name:
                return [float(child[0].text), float(child[1].text)]
        elif child.tag == type and type == "misc":
            if child.attrib["name"] == name:
                return child[0].text

icor = parse_root("icor", "geometry")
ich = parse_root("ich", "geometry")
ocor = parse_root("ocor", "geometry")
ocir = parse_root("ocir", "geometry")
och = parse_root("och", "geometry")

cal_dynamo = parse_root("dynamo", "calibration")
cal_30AHES = parse_root("30AHES", "calibration")
cal_5AHES = parse_root("5AHES", "calibration")

cal_IcoVms = parse_root("IcoVms", "calibration")
cal_TsVms = parse_root("TsVms", "calibration")
cal_TauIemf = parse_root("TauIemf", "calibration")

calc_supply_voltage = [0.066, 2.422]

cal_Vnl = [5.130, 15.275]

version = parse_root("version", "misc")

def writeout(path="./../etc/data.xml"):
    '''
    resx.writeout(**kwargs)
    
    Writes the contents of a data file.
    
    **kwargs:
        path        (string)        Path to data.xml. Default is './../etc/data.xml'
    '''
    global root
    # update xml tree
    
    # geometries
    root[0][0].text = str(icor)
    root[1][0].text = str(ich)
    root[2][0].text = str(ocor)
    root[3][0].text = str(ocir)
    root[4][0].text = str(och)
    # calibrations
    root[5][0].text = str(cal_dynamo[0])
    root[5][1].text = str(cal_dynamo[1])
    root[6][0].text = str(cal_30AHES[0])
    root[6][1].text = str(cal_30AHES[1])
    root[7][0].text = str(cal_5AHES[0])
    root[7][1].text = str(cal_5AHES[1])
    root[8][0].text = str(cal_TauIemf[0])
    root[8][1].text = str(cal_TauIemf[1])
    root[9][0].text = str(cal_IcoVms[0])
    root[9][1].text = str(cal_IcoVms[1])
    
    tree = ET.ElementTree(root)
    tree.write(path)

def get_current(cr, cr2a, cr2b):
    '''
    resx.get_current(cr, cr2a, cr2b)
    
    Given the outputs from three current sensors, calculates the current.
    
    Parameters:
        cr      (list, float)       List of 30A HECS voltage readings
        cr2a    (list, float)       List of 5A HECS voltage readings
        cr2b    (list, float)       List of 5A HECS voltage readings
    
    Returns:
        cu      (list, float)       List of current values, averaged out from three sensors.
    '''
    cu1 = cal_30AHES[0] * cr + cal_30AHES[1]
    cu2 = cal_5AHES[0] * cr2a + cal_5AHES[1]
    cu3 = cal_5AHES[0] * cr2b + cal_5AHES[0]
    
    cu = cu1 + cu2 + cu3
    cu = cu / 3.0
    
    return cu
    
def get_speed_rpm(dr):
    '''
    resx.get_speed_rpm(dr)
    
    Given readings from a dynamo, uses calibration data stored in data.xml to calculate the rotational speed in
    RPM of the motor.
    
    Parameters:
        dr      (list, float)       List of dynamo voltage readings.
    
    Returns:
        v_rpm   (list, float)       List of speeds in RPM.
    '''
    v_rpm = dr * cal_dynamo[0] + cal_dynamo[1]
    return v_rpm

def get_speed_rads(dr):
    '''
    resx.get_speed_rads(dr)
    
    Given readings from a dynamo, uses calibration data stored in data.xml to calculate the rotational speed in
    radians per second of the motor.
    
    Parameters:
        dr      (list, float)       List of dynamo voltage readings.
    
    Returns:
        v_rads  (list, float)       List of speeds in rad/s.
    '''
    v_rpm = get_speed_rpm(dr)
    v_rads = v_rpm * np.pi / 30 # rpm is 2pi per 60s =~ 1/10 rad/s
    return v_rads
    
def get_supply_voltage(pv):
    '''
    resx.get_supply_voltage(pv)
    
    Given a list of the values sent to the potentiometer, calculates the supply voltage to the motor.
    
    Parameters:
        pv      (list, integer)     List of values sent to potentiometer.
    
    Returns:
        voltage (list, float)       List of motor supply voltages.
    '''
    voltage = pv * calc_supply_voltage[0] + calc_supply_voltage[1]
    return voltage

def get_current_coil(pv):
    '''
    resx.get_current_coil(pv)
    
    Given a list of the values sent to the potentiometer, uses calibration data stored in data.xml to 
    calculate the current loss due to inefficiency (Icoil).
    
    Parameters:
        pv      (list, float)       List of values sent to potentiometer.
    
    Returns:
        ico     (list, float)       List of coil currents.
    '''
    voltage = get_supply_voltage(pv)
    ico = cal_IcoVms[0] * voltage + cal_IcoVms[1]  # Ico = (1/Rco) * Vms + (~0.0)
    return ico

def get_torque(stress, fill_volume_ml):
    '''
    resx.get_torque(stress, fill_volume_ml)
    
    Calculates the torque from stress and fill data.
    
    Parameters:
        stress          (list, float)   List of stresses
        fill_volume_ml  (number)        Volume of test fluid in ml.
    
    Returns:
        T       (list, float)       List of torques.
    '''
    H = (fill_volume_ml * 0.000001) / ((pi * self.ocir * self.ocir) - (pi * self.icor * self.icor)) # height = volume / area
    T = 2 * pi * self.icor * self.icor * H
    return T
    
if __name__ == "__main__": print __doc__
