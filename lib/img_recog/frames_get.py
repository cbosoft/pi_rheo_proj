import subprocess as sp
import glob
import os

vids = sorted(glob.glob("videos/*.avi"))

if (len(vids) < 1):
    print("There are no videos to convert to frames!")
    exit()

start_time = int(vids[0][7:-6])

if (len(glob.glob("working_frames/*")) == 0):
    for vid in vids:
        file_start_time = int(vid[7:-6])
        os.mkdir("working_frames/" + str(file_start_time))
        sp.call(["avconv -i " + vid + " -f image2 working_frames/" +
        str(file_start_time) + "/%06d.jpg"], shell=True)

starts = sorted(glob.glob("working_frames/*"))
first_start = int(starts[0][15:])
frame_counter = 0

for start in starts:
    frames = sorted(glob.glob(start + "/*.jpg"))
    for frame in frames:
        frame_time = (int(start[15:]) + frame_counter * 33) - first_start
        frame_index = frame_counter
        os.rename(frame, "frames/" + str(frame_index).zfill(6) +
        str(round(int(frame_time)))[:-2] + ".jpg")
        frame_counter += 1
