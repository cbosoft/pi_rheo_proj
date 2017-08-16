# RPi-R #

Raspberry Pi Rheometer. A rheometer using a Taylor-Couette cell along with 
a plethora of sensors to record a bunch of data like temperature, revolution
speed, motor supply current etc etc.

The project has been extended, so more effort can be put into designing the 
hardware.

With now a choice of motor and what-have-you, a better (read: working) rheometer
can be produced in the next few months. A few different design are being considered,
one possible novel method which could be cool (although there is nothing new under
the sun, someone must have tried it before).

I have started with a software overhaul, and will continue to ponder what direction
to go in with the hardware until October, when I will begin to put plans into action.


## Changelog ##

**v0.1.5**

- Cleaned up gui
- Rewrote recalibration algo
- Added cal override (if cal is wrong or previous was better whatever)
- General tidying of script
- Removed quick run as an option (when would this ever be used?)
- Added info about why each package is being imported
- Removed "Plot" as a main menu option - this may return later on
- Removed complex menu system
- Removed rheometry calculation function (was incorrect anyway)


```
/bin                            code lives here
/etc/data.xml                   meta data lives here (calibrations, rheometer geometry)
/logs                           data logged from experimental runs lives here (temporary)
/misc/datasheets                hardware datasheets live here
/plot                           scripts for plotting results live here
```
*Distributed under GNU General Public License (GPL).*

*You can use this as much as you like, share it as you like, whatever.*

*However, there is no warranty or guarantee that it will actually work.*
