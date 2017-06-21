### RPi-R ###

Raspberry Pi Rheometer. A rheometer using a Taylor-Couette cell along with 
a plethora of sensors to record a bunch of data like temperature, revolution
speed, motor supply current etc etc.

Due to time constraints and difficulty of getting the rheometer to work properly 
(i.e. it doesn't accurately report viscosity vs time and I can't be bothered to
fix it), The rheometer will now be used simply as a rough guide. The power into 
the motor is directly related to the torque output, and therefore (at constant
strain rate) the viscosity. The rheometer will normalise the power draw with 
respect to the empty rheometer.

The important part here is how the piezo-sensor output and the normal rheometer 
output match up.

TO DO:
* Attach piezo sensors in such a way as to minimise noise (i.e. from motor)
* Re-write software to reflect new simplified method of indication
* Figure out best method for plotting results
* ~~Calibration scripts~~
* ~~Central calibration storage (not as var in each class!)~~
* ~~Redo cals (TS vs. Vms & Iemf vs.  Vms)~~
* ~~Analogue filtering?~~ Not necessary, might implement later
* Dead-time compensation?
* Speed control
* ~~Temperature control (monitoring)~~


```
/bin                            code lives here
/etc                            meta data lives here (calibrations, rheometer geometry)
/logs                           data logged from experimental runs lives here (temporary)
/misc/datasheets                hardware datasheets live here
/plot                           scripts for plotting results live here
```
*Distributed under GNU General Public License (GPL).*

*You can use this as much as you like, share it as you like, whatever.*

*However, there is no warranty or guarantee that it will actually work.*
