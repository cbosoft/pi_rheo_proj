# custom_libs: Custom Libraries

I'm using a Raspberry Pi to control an experiment, using the scripts posted here. WIP.

```
overall_loop.py           uses the other libs to achieve the main task

/datasheets               contains the datasheets for the hardware used

/img_recog_templates      images here used to develop the image recognition script

/lib/adc.py               py class for using the MCP2434 adc chip
/lib/control.py           py class for creating a simple PID controller
/lib/crack_det.py         py method for recognising the presence of cracks in the image
/lib/dac.py               blank atm
/lib/motor.py             (incomplete) py class for using a motor with the raspberry pi
/lib/v_reg.py             (incomplete) py class to control the voltage supplied to a motor
```
*You can use this as much as you like, share it as you like, whatever. There's no warranty or guarantee that it will actually work.*
