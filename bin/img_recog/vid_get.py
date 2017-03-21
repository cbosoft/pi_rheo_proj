import subprocess as sp
import glob
import time

# TODO: edit for multiple runs

end_time = int(600 * 1000)  # milliseconds
max_time = int(55 * 60 * 1000)  # max recording length the program can deal with

if (end_time > max_time):
    print("The run time is too long, the max allowable is 55 minutes. Please reduce.")
    exit()

vid_length = 10  # seconds
start_time = int(round(time.time() * 1000))

if (len(glob.glob("videos/*")) > 0):
    print(("There are already videos in the output folder. Remove them to recor"
    + "d more"))
    exit()

finished = False
while (not finished):
    vid_start = int(round(time.time() * 1000)) - start_time
    sp.call(["avconv -f video4linux2 -t " + str(vid_length) + " -i /dev/video0 "
    + "videos/" + str(round(int(vid_start))) + ".avi"], shell=True)
    #time.sleep(3)
    if ((time.time() * 1000) >= (start_time + end_time)):
        finished = True
