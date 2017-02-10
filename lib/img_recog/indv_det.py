# runs the imgproc on the files which match the filter

import crack_det
import glob
import os
import sys


def do(number):
    log = open("outp/log_mod_" + str(number), 'w')
    os.chdir("frames")
    files = sorted(glob.glob("*.bmp"))
    file_cnt = len(files)
    for file in files:
        try:
            # filename should be [index][timestamp][.bmp]
            img_num = int(file[:6])
            img_timestamp = int(file[6:-4])
            if (img_num % 4 == number):
                if (number == 0):
                    prog = (img_num * 100) / file_cnt
                    sys.stdout.write(('\r[ {0} ] {1}%').format(str('#' * (prog / 2)) + str(' ' * (50 - (prog / 2))), prog))
                    sys.stdout.flush()
                (res, crack_amnt) = crack_det.crack_det(file, 245, 15, 0, True)
                if (res):
                    log.write("1,")
                else:
                    log.write("0,")
                log.write(str(img_timestamp) + "," + str(crack_amnt) + "," + file + "\n")
        except TypeError:
            pass  # file name is not a number
    log.write("EOF")
    log.close()
