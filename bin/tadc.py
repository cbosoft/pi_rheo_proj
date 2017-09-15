from time import sleep 
from adc import MCP3008

adc = MCP3008(vref=5.0)

for i in range(0, 100):
    str_ = ""
    for j in range(0, 8):
        str_ += "|    c{}: {:.2f}    ".format(j, adc.read_volts(j))
    print str_
    sleep(1)
