# Reads a value from the ADC, shows on screen, updates
import sys
sys.path.append('./..')

from adc import MCP3424
import time
import os

adc = MCP3424(0x6e, 3, 0, 0)
doing = True
while (doing):
	try:
		os.system('clear')
		print ("Value: {}").format(adc.read_single())
		time.sleep(0.1)
	except	KeyboardInterrupt:
		doing = False		
