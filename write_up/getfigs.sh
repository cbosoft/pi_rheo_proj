#!/bin/bash
cd ./figures
for f in `dir -d *.py`
do
 echo "Processing $f"
 python $f
done
