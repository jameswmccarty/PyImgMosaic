#!/usr/bin/python3.5

# Viewer for color data

# Requires vpython to be installed, which itself requires jupyter
# http://vpython.org/
# https://jupyter.org/

# Launches a web browser and draws a cube with dimensions 255 units per size
# End points are large spheres of maximum RGB value at that point on the cube
# Scans scaled image library, and puts a smaller sphere of the correct color
# in the color cube.  Can be helpful to see where gaps in color coverage are.


from PIL import Image
from vpython import *
import os
import sys

tilesize = None
source_path = "./img_scaled/"
spheres = []

# returns average (r, g, b) value tuple for an an image
def rank_image(im):
	r, g, b = 0, 0, 0
	w, h = im.size
	im = im.load()
	d = w * h
	for x in range(w):
		for y in range(h):
			r += im[x,y][0]
			g += im[x,y][1]
			b += im[x,y][2]
	return (r/d, g/d, b/d)

def print_usage():
	print("Call with -s <tilesize>")
	exit()

if __name__ == "__main__":

	if '-s' not in sys.argv:
		print_usage() # show proper format and exit

	# Read user set parameter, and update source path
	tilesize = int(sys.argv[sys.argv.index('-s') + 1])
	source_path += str(tilesize) + "/"

	autoscale = True # for scene


	# Draw 8 boundary points on the cube
	spheres.append(sphere(pos=vector(0,0,0), radius=5., color=vector(0,0,0)))
	spheres.append(sphere(pos=vector(0,0,255), radius=5., color=vector(0,0,1)))
	spheres.append(sphere(pos=vector(0,255,0), radius=5., color=vector(0,1,0)))
	spheres.append(sphere(pos=vector(255,0,0), radius=5., color=vector(1,0,0)))
	spheres.append(sphere(pos=vector(255,255,0), radius=5., color=vector(1,1,0)))
	spheres.append(sphere(pos=vector(255,0,255), radius=5., color=vector(1,0,1)))
	spheres.append(sphere(pos=vector(0,255,255), radius=5., color=vector(0,1,1)))
	spheres.append(sphere(pos=vector(255,255,255), radius=5., color=vector(1,1,1)))

	# Scan filenames and average RGB values
	for filename in os.listdir(source_path):
		print("Processing " + filename)
		im = Image.open(source_path+filename)
		if im.mode is not 'RGBA' or 'RGB': # prevent errors with B&W images
			im = im.convert('RGB')		
		rgb = rank_image(im)
		pos   = vector(int(rgb[0]), int(rgb[1]), int(rgb[2]))
		color = vector(rgb[0]/255., rgb[1]/255., rgb[2]/255.) # max color unit is 1.0
		print(color)
		im.close()
		spheres.append(sphere(pos=pos, color=color)) # populate display

