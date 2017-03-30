# Imports
import pygame.camera
import pygame.image
from time import time
import glob, os

# Init camera
print "Initialising camera..."
pygame.camera.init()
cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
cam.start()
start_time = time()
run_frm_cnt = 0

# Empty frames directory
files = glob.glob("frames/*")
for f in files:
        os.remove(f)

# loop
try:
	while True:
		print "Getting image data from camera..."
		cam.get_image()
		cam.get_image()
		img = cam.get_image()
		# file name should be:
		# [index][timestamp][.bmp]
		pygame.image.save(img, "frames/" + str(run_frm_cnt).zfill(6) + str(int((time() - start_time) * 1000)) + ".bmp")
		run_frm_cnt += 1
except KeyboardInterrupt:
	pygame.camera.quit()
