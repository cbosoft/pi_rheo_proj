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
from PIL import Image  # uses python imaging library (PIL v1.1.7 for python 2.7)

def crack_det(path, BGT=245, crack_thresh=5, verbose=False):
    if (verbose):
        print("Edge detection begninning...")

    image = Image.open(path)                                                     # set up working variables
    image = image.convert("L")
    pixels = image.load()                                                        # get image pixel data
    image_edge = Image.new("L",image.size)                                     # create edge image the same size as the working image
    pixels_edge = image_edge.load()                                              # create handler for edge detected image's pixel data
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

            if (length <= BGT):							# if the intensity is below a threshhold, set to black and update number of crack pixels
                length = 0
                crack_px += 1

            pixels_edge[x, y] = length	# draw the length in the edge image

    if (verbose):
        print("Crack amount:" + str(((crack_px * 100) / total_px)) + "%")
        image_edge.save("edge.bmp")
        image.save("mono.bmp")
    if (((crack_px * 100) / total_px) >= crack_thresh): # If more than threshhold amount of black (edges), set cracks fround to True
        return True
    else:
        return False