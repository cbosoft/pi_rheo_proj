#!/bin/bash
echo "Plotting figures"
cd ./plot
arr=(*.py)
count=${#arr[@]}

#for f in `dir -d *.py`
for i in $(seq 1 $count)
do
 echo "($i/$count) Processing: ${arr[$i - 1]}"
 python ${arr[$i - 1]}
done
