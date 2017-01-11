#!/bin/bash

echo cleaning up...
rm -rf /var/www/html/lib &> /dev/null
rm /var/www/html/overall_loop.py &> /dev/null

echo copying over files....
#cp -rf /home/pi/Gits/pi_rheo_proj/lib /var/www/html/lib &> /dev/null
mkdir /var/www/html/lib
cp /home/pi/Gits/pi_rheo_proj/lib/* /var/www/html/lib &> /dev/null
cp /home/pi/Gits/pi_rheo_proj/overall_loop.py /var/www/html/overall_loop.py &> /dev/null
echo finished!
