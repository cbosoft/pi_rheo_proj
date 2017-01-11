#
# Master program
# Uses the other libraries to control the experiment and record the data

# Imports
import sys
sys.path.insert(0, "lib")
import exp_run
from glob import glob
import os

runs_to_do = True

#loop:
while (runs_to_do):
    runs = sorted(glob.glob("run_data/*.nd"))
    if (len(runs) > 0):
        run_data = open(runs[0], "r")  # open run data
        #TODO  # get run data
        run_ = exp_run.run()  # initialise the run
        run_data.close()  # close the data file

        os.rename(runs[0], runs[0][:-2] + "ip")  # set run as in progress
        run_.start_run()  # begin th experiment

        os.rename(runs[0], runs[0][:-2] + "d")  # set run as done
    else:
        runs_to_do = False

print("All runs completed!")