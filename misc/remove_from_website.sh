#!/bin/bash

echo cleaning up...
rm -rf /var/www/html/lib &> /dev/null
rm /var/www/html/overall_loop.py &> /dev/null
echo finished!
