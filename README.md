I'm using a Raspberry Pi to control a custom built rheometer.

Useful links:

Learn Python:
    https://en.wikibooks.org/wiki/Non-Programmer%27s_Tutorial_for_Python_2.6/Intro

More Learn Python:
    http://www.pyschools.com/

(I will update with more links as I go)


TO DO:
* Calibration scripts
* Central calibration storage (not as var in each class!)
* Redo cals (TS vs. Vms & Iemf vs.  Vms)
* Analogue filtering?
* Dead-time compensation?
* Speed control
~~* Temperature control (monitoring)~~


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
