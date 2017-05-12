# 
# Resources
# 
# Returns data about the rheometer (geomettry, calibrations)

import xml.etree.ElementTree as ET

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

icor = parse_root("icor", "geometry")
ich = parse_root("ich", "geometry")
ocor = parse_root("ocor", "geometry")
ocir = parse_root("ocir", "geometry")
och = parse_root("och", "geometry")

cal_dynamo = parse_root("dynamo", "calibration")
cal_30AHES = parse_root("30AHES", "calibration")
cal_5AHES = parse_root("5AHES", "calibration")

def writeout(path="./../etc/data.xml"):
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
    tree = ET.ElementTree(root)
    tree.write(path)