#
# adc.py Test Script
#
# Reads a value from the ADC, shows on screen, updates
#

import sys
sys.path.append('./..')

from adc import MCP3424
import time

adc = MCP3008()
doing = True

while (doing):
	try:
        sys.stdout.write(('ADC Value: {0}').format(adc.read_data()))
        sys.stdout.flush()
		time.sleep(0.1)
	except	KeyboardInterrupt:
		doing = False		
