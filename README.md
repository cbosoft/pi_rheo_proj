# custom_libs

I'm using a Raspberry Pi to control an experiment, using the scripts posted here. WIP.

```
overall_loop.py                 uses the other libs to achieve the main task

/datasheets                     contains the datasheets for the hardware used

/img_recog_templates            images here used to develop the image recognition script

/lib/adc.py                     py class for using the MCP2434 adc chip
/lib/control.py                 py class for creating a simple PID controller
/lib/dac.py                     blank atm
/lib/motor.py                   (incomplete) py class for using a motor with the raspberry pi
/lib/v_reg.py                   (incomplete) py class to control the voltage supplied to a motor

/lib/img_recog                  contains scripts and files used and output by the crack detection script
/../do*.py                      used to start crack detection script in different threads, for faster processing
/../bulk_det.py                 launches the processes in multiple threads and waits for them the complete
/../indv_det.py                 actually performs the detection and updates progress to stdout
/../frames_record.py            used for debugging. captures frames from a webcam and saves the frames
/../outp/dat.csv                csv with the output from the crack detection script:
                                [cracks found (0 or 1)],[time, ms],[crack probability],[frame]
```
*You can use this as much as you like, share it as you like, whatever. There's no warranty or guarantee that it will actually work.*
