import adclib

adc = mpc3424(0x6e, 0, 0, 0)
b = adc.read_data()
print b