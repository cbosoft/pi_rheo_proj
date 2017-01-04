from adclib import mpc3424
import time
import os

adc = mpc3424(0x6e, 0, 0, 0)
doing = True
while (doing):
	try:
		os.system('clear')
		print ("Value: {}").format(adc.read_data())
		time.sleep(0.1)
	except	KeyboardInterrupt:
		doing = False		
