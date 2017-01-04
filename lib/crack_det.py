#
# Crack Detection Support
#
# Thanks to the university of cambridge:
# http://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/image-processing/edge_detection.html
#
#
# for future implementation:
# https://en.wikipedia.org/wiki/Canny_edge_detector
#

# Imports
import math  # s
from PIL import Image # uses python imaging library (PIL v1.1.7 for python 2.7)

def crack_det(path, BGT=245, crack_thresh=5, verbose_level=0, mono=False):
	#verbose_level: how much info will the script send to cli
	#				0-> nothing
	#				1-> small notices of when stuff is beginning
	#				2-> output of images used in during the process ("edge.bmp" -> edge detected image, "mono.bmp" -> monochrome version of the frame)
	#				3-> insanely high output of messages, useful for debugging
	if (verbose_level > 0):
		print("Crack detection beginning")
	
	if (verbose_level > 2):
		print("Loading image")
	image = Image.open(path)							# set up working variables
	
	if (mono):
		if (verbose_level > 2):
			print("Converting to monochrome")
		image=image.convert("L")
	
	if (verbose_level > 2):
		print("Loading pixel data")
	pixels = image.load()								# get image pixel data
	
	if (mono):
		image_edge = Image.new("L",image.size)			# create edge image the same size as the working image
	else:
		image_edge = Image.new("RGB",image.size)		# create edge image the same size as the working image
	
	pixels_edge = image_edge.load()						# create handler for edge detected image's pixel data
	
	if (verbose_level > 2):
		print("Calculating number of pixels")
	total_px = image.size[0] * image.size[1]			# total number of pixels
	crack_px = 0										# number of pixels which are thought to be in a crack
	
	if (verbose_level > 2):
		print("Beginning pixel iteration")
		
	for x in range(1, image.size[0] - 1):
		for y in range(1, image.size[1] - 1):
			Gx = 0										# x direction gradient, initially 0
			Gy = 0										# y direction gradient, initially 0
			
			if (mono):
				# column left of current pixel
				intensity = pixels[x - 1, y - 1]
				Gx -= intensity
				Gy -= intensity

				intensity = pixels[x - 1, y]
				Gx -= intensity
				Gx -= intensity

				intensity = pixels[x - 1, y + 1]
				Gx -= intensity
				Gy += intensity

				# pixels above and below current pixel
				intensity = pixels[x, y - 1]
				Gy -= intensity
				Gy -= intensity

				intensity = pixels[x, y + 1]
				Gy += intensity
				Gy += intensity

				# column right of current pixel
				intensity = pixels[x + 1, y - 1]
				Gx += intensity
				Gy -= intensity

				intensity = pixels[x + 1, y]
				Gx += intensity
				Gx += intensity

				intensity = pixels[x + 1, y + 1]
				Gx += intensity
				Gy += intensity

				# calculate the length of the gradient, normalise the length of gradient to the range 0 to 255 convert the length to an integer and invert
				length = 255 - int((math.sqrt((Gy * Gy) + (Gx * Gx)) * 255) / 1443)
			else:
				# column left of current pixel
				r, g, b = pixels[x - 1, y - 1]
				intensity = (r + g + b)
				Gx -= intensity
				Gy -= intensity
				
				r, g, b = pixels[x - 1, y]
				intensity = (r + g + b)
				Gx -= intensity
				Gx -= intensity

				r, g, b = pixels[x - 1, y + 1]
				intensity = (r + g + b)
				Gx -= intensity
				Gy += intensity

				# pixels above and below current pixel
				r, g, b = pixels[x, y - 1]
				intensity = (r + g + b)
				Gy -= intensity
				Gy -= intensity

				r, g, b = pixels[x, y + 1]
				intensity = (r + g + b)
				Gy += intensity
				Gy += intensity

				# column right of current pixel
				r, g, b = pixels[x + 1, y - 1]
				intensity = (r + g + b)
				Gx += intensity
				Gy -= intensity

				r, g, b = pixels[x + 1, y]
				intensity = (r + g + b)
				Gx += intensity
				Gx += intensity

				r, g, b = pixels[x + 1, y + 1]
				intensity = (r + g + b)
				Gx += intensity
				Gy += intensity
				
				# calculate the length of the gradient, normalise the length of gradient to the range 0 to 255 convert the length to an integer and invert
				length = 255 - int((math.sqrt((Gy * Gy) + (Gx * Gx)) * 255) / 4328)
			
			if (length <= BGT):  # if the intensity is below a threshhold, set to black and update number of crack pixels
				length = 0
				crack_px += 1
			
			pixels_edge[x, y] = (length, length, length)  # draw the length in the edge image
	
	if (verbose_level > 1):
		image_edge.save("edge.bmp")
		if (mono):
			image.save("mono.bmp")
		
	if (((crack_px * 100) / total_px) >= crack_thresh):  # If more than threshhold amount of black (edges), assume cracks found
		if (verbose_level > 0):
			print(("Detection complete (" + str(((crack_px * 100) / total_px)) + "%, cracks found)"))
		return True
	else:
		if (verbose_level > 0):
			print(("Detection complete (" + str(((crack_px * 100) / total_px)) + "%)"))
		return False