/bin/*
----

Contains the python classes and scripts used to run the rheometer:

```
adc.py                manages an MCP3008 ADC from a Raspberry Pi
control.py            simple implementation of PI controller in python
dig_pot.py            manages an MCP4131 digital potentiometer from a Raspberry Pi
filter.py             simple implementation of various low-pass filters using scipy
motor.py              manages a motor using an ADC to read sensor data, and an MCP4131 to control power supply
plothelp.py           simple functions that make things easier to plot
resx.py               manages the loading and saving of essential calibration and geometry data
rheometer.py          uses everything else to manage the rheometer from the raspberry pi (RUN THIS ONE)
tempsens.py           manages the use of a DS18B20 temperature sensor from a raspberry pi
```
