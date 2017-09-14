from time import sleep
from adc import MCP3008

adc = MCP3008()


for i in range(0, 100):
    print adc.read_volts(0), (adc.read_volts(0) + 1.0)
    sleep(1)
