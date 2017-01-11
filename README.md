I'm using a Raspberry Pi to control an experiment, using the scripts posted here. WIP.

```
overall_loop.py                 uses the other libs to achieve the main task

/datasheets                     contains the datasheets for the hardware used

/img_recog_templates            images here used to develop the image recognition script

/lib/adc.py                     py class for using the MCP2434 adc chip
/lib/control.py                 py class for creating a simple PID controller
/lib/dig_pot.py                 py class for using an MCP4531 digital potentiometer with the raspberry pi (to control motor speed)
/lib/motor.py                   py class for using a motor with the raspberry pi (uses dig_pot.py)

/lib/img_recog                  contains scripts and files used and output by the crack detection script
/../do*.py                      used to start crack detection script in different threads, for faster processing
/../bulk_det.py                 launches the processes in multiple threads and waits for them the complete
/../indv_det.py                 actually performs the detection and updates progress to stdout
/../frames_record.py            used for debugging. captures frames from a webcam and saves the frames
/../outp/dat.csv                csv with the output from the crack detection script:
                                [cracks found (0 or 1)],[time, ms],[crack probability],[frame]
/../vid_get.py                  repeatedly records 10 minutes of video from the main video device attached (usb webcam etc) 
                                and saves with the timestamp as the filename.
/../frames_get.py               converts the recorded video files to individual frames to enable the image recognition to be run
```
*You can use this as much as you like, share it as you like, whatever. There's no warranty or guarantee that it will actually work.*
