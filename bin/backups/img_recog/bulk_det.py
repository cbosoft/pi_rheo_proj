# runs 4 image processing scripts
# hopefully this will speed up the overall process by using all 4 CPU threads

# Imports
import subprocess as sp
import os
import sys

image_dir = "frames"
dat_dir = "outp"

# create the 4 relevant log files
for i in range(0, 4):
    log = open(dat_dir + "/log_mod_" + str(i), "w")
    log.close()

# start the four processes
for i in range(0, 4):
    sp.Popen("sudo python ./do" + str(i) + ".py", shell=True)

print("Working...")

# check if the process is complete
done = False
while (not done):
    try:
        done = True
        for i in range(0, 4):
            log = open(dat_dir + "/log_mod_" + str(i), "r")
            lines = log.readlines()
            if lines:
                pass
            else:
                done = False
    except IOError:
        pass

# merge with the four created data log files
prog = 100
sys.stdout.write(('\r[ {0} ] {1}%').format(str('#' * (prog / 2)) + str(' ' * (50 - (prog / 2))), prog))
sys.stdout.flush()
print("\nMerging log files...")
log_0 = open(dat_dir + "/log_mod_0", "r")
log_1 = open(dat_dir + "/log_mod_1", "r")
log_2 = open(dat_dir + "/log_mod_2", "r")
log_3 = open(dat_dir + "/log_mod_3", "r")

lines_0 = log_0.readlines()
lines_1 = log_1.readlines()
lines_2 = log_2.readlines()
lines_3 = log_3.readlines()

log_0.close()
log_1.close()
log_2.close()
log_3.close()

log_all = open(dat_dir + "/dat.csv", "w")

done_0 = False
done_1 = False
done_2 = False
done_3 = False

pos = 0

while (not (done_0 and done_1 and done_2 and done_3)):
    if not done_0:
        if lines_0[pos] == "EOF":
            done_0 = True
        else:
            log_all.write(lines_0[pos])
    if not done_1:
        if lines_1[pos] == "EOF":
            done_1 = True
        else:
            log_all.write(lines_1[pos])
    if not done_2:
        if lines_2[pos] == "EOF":
            done_2 = True
        else:
            log_all.write(lines_2[pos])
    if not done_3:
        if lines_3[pos] == "EOF":
            done_3 = True
        else:
            log_all.write(lines_3[pos])
    pos += 1
log_all.close()
print("Deleting surplus log files..")

os.remove(dat_dir + "/log_mod_0")
os.remove(dat_dir + "/log_mod_1")
os.remove(dat_dir + "/log_mod_2")
os.remove(dat_dir + "/log_mod_3")
print("Done!")
