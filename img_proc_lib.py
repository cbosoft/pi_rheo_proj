#
# Image processing class
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

# Image_Processor class will take an image
class Image_Processor(object):
	img = Image.New("RGB",[10,10],[0,0,0])					# image object used by the methods in this class
	pix = img.load()										# pixel data for the image
	img_edge = img											# edge detected image
	pix_edge = img_edge.Load()								# pixel data for the edge detected image
	crack_found = False										# has a crack been identified in the image?
	
	# initialisation method
	def __init__(self):
		self.img = Image.New("RGB",[10,10],[0,0,0])			# creates a temporary blank small image
		self.pix = self.img.load()							# gets pixel data
		self.img_edge = self.img							# creates a placeholder for the edge detected image
		self.pix_edge = self.img_edge.Load()				# and gets image data for the edge detected image
		self.crack_found = False							# initially no cracks found
	
	# sets new image in processor
	def set_img(self, path):
		self.img = Image.open(path)
		self.pix = img.Load()
		self.img_edge = edge_det()
		self.pix_edge = img_edge.Load()
		self.crack_found = False
	
	# apply edge detection algorithm
	def edge_det(self, image=self.img, BGT=245, crack_thresh=15):
															# set up working variables
		pixels = image.load()								# get image pixel data
		image_edge = image									# create edge image the same size as the working image
		pixels_edge = image_edge.load()						# create handler for edge detected image's pixel data
		total_px = image.size[0] * image.size[1]			# total number of pixels
		crack_px = 0										# number of pixels which are thought to be in a crack
		
		for x in range(1, image.size[0] - 1):
			for y in range(1, image.size[1] - 1):
				Gx = 0										# x direction gradient, initially 0
				Gy = 0										# y direction gradient, initially 0

															# Sobel Kernal: x direction
															# -1  0  1
															# -2  0  2
															# -1  0  1
															
															# Sobel Kernal: y direction
															# -1 -2 -1
															#  0  0  0
															#  1  2  1
															
															# apply the sobel kernals to the image
															
															# column left of current pixel
				r, g, b = pixels[x - 1, y - 1]
				Gx += -(r + g + b)
				Gy += -(r + g + b)
				
				r, g, b = pixels[x - 1, y]
				Gx += -2 * (r + g + b)

				r, g, b = pixels[x - 1, y + 1]
				Gx += -(r + g + b)
				Gy += (r + g + b)

															# pixels above and below current pixel
				r, g, b = pixels[x, y - 1]
				Gy += -2 * (r + g + b)

				r, g, b = pixels[x, y + 1]
				Gy += 2 * (r + g + b)

															# column right of current pixel
				r, g, b = pixels[x + 1, y - 1]
				Gx += (r + g + b)
				Gy += -(r + g + b)

				r, g, b = pixels[x + 1, y]
				Gx += 2 * (r + g + b)

				r, g, b = pixels[x + 1, y + 1]
				Gx += (r + g + b)
				Gy += (r + g + b)

				length = math.sqrt((Gx * Gx) + (Gy * Gy))	# calculate the length of the gradient

				length = length / 4328 * 255				# normalise the length of gradient to the range 0 to 255

				length = 255 - int(length)					# convert the length to an integer and invert
				
				if (length <= BGT):							# if the intensity is below a threshhold, set to black and update number of crack pixels
					length = 0
					crack_px += 1
				
				pixels_edge[x, y] = length, length, length	# draw the length in the edge image
		
		if (image == self.image):							# if the img was the class local, set the local outputs
			self.img_edge = image_edge
			self.pix_edge = pixels_edge
			
			if (((crack_px * 100) / total_px) > crack_thresh): # If more than threshhold amount of black (edges), set cracks fround to True
				self.crack_found = True
		
		return pixels_edge
	
	# runs edge detection and gets whether a crack was found
	def crack_det(self, image_path, BGT=245, crack_thresh=15):
		self.set_img(image_path)
		self.edge_det(self.img, BGT, crack_thresh)
		return self.crack_found