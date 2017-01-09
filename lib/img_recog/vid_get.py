import subprocess as sp
import glob
import time

end_time = 60000
vid_length = 10
start_time = int(round(time.time() * 1000))

if (len(glob.glob("videos/*")) > 0):
    print(("There are already videos in the output folder. Remove them to recor"
    + "d more"))
    exit()

finished = False
while (not finished):
    vid_start = round(int(time.time() * 1000)) - start_time
    sp.call(["avconv -f video4linux2 -t " + str(vid_length) + " -i /dev/video0 "
    + "videos/" + str(round(int(vid_start))) + ".avi"], shell=True)
    #time.sleep(3)
    if ((time.time() * 1000) >= (start_time + end_time)):
        finished = True
