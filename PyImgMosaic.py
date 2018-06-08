#!/usr/bin/python

# This utility reproduces an image from many other
# smaller image 'tiles.'

from PIL import Image
import os
import sys
from subprocess import call
from math import sqrt

""" Create a directory called 'img_src' in the same
location as this script.  Populate this directory with
images that you want to use as small tiles. """

""" Invoke this program with two mandatory command line args
    and one optional third argument:
	1) The image file to reproduce.
	2) The size of tile to use in the reproduction
    3) An error threshold, that when exceed, adds previously
       used tiles back into the mix of available tiles.  

Example: python PyImgMoasic.py moon.jpg 16

Output is written to filename_out.png, i.e. 
 moon_out.png.

"""

target_img  = None
tiles = {} # key is filename, value is avg RGB
discarded = {} # store for used images
tilesize = None
threshold = 66 # determined by experimenting
source_path = "./img_scaled/"

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

# returns mean squared error between two (r, g, b) values
def pxl_dist(a, b):
	ssd  = (a[0]-b[0])**2
	ssd += (a[1]-b[1])**2
	ssd += (a[2]-b[2])**2
	return sqrt(ssd)

def best_match(val):
	global tiles
	global discarded
	global threshold
	err = 1e9
	match = None
	for k,v in tiles.items():
		# find the closest match in our dictionary
		score = pxl_dist(val, v)
		if score < err:
			err = score	
			match = k
	if match == None or err > threshold: # ran out of good images
		print("Tripped error threshold.")	
		tiles.update(discarded) # put previously discarded images back in play
		discarded = {}
		for k,v in tiles.items():
		# check again
			score = pxl_dist(val, v)
			if score < err:
				err = score	
				match = k
	if match == None or err > threshold: # no options. giving up.
		print("Error: No tiles, or can't meet error threshold.")
		exit()
	return match

if __name__ == "__main__":

	if len(sys.argv) < 3:
		print("Usage: python PyImgMoasic.py filename tilesize [error]")
		print("Example: python PyImgMoasic.py moon.jpg 16")
		print("Default value for error is 66.")
		exit()

	# Read user set parameters, and update source path
	target_img = sys.argv[1]
	tilesize = int(sys.argv[2])
	if len(sys.argv) > 3:
		threshold = int(sys.argv[3])
	source_path += str(tilesize) + "/"
	
	# Use bash script and ImageMagic for conversion process
	print("Generating tile images...")
	call(["./scaler.sh", str(tilesize)])

	# Add filenames and average RGB values to a dictionary called tiles
	for filename in os.listdir(source_path):
		print("Processing " + filename)
		im = Image.open(source_path+filename)
		if im.mode is not 'RGBA' or 'RGB': # prevent errors with B&W images
			im = im.convert('RGB')		
		rgb = rank_image(im)
		im.close()
		tiles.update({filename:rgb})

	target = Image.open(target_img) # This is the image to reproduce
	if target.mode is not 'RGBA' or 'RGB': # prevent errors with B&W images
		target = target.convert('RGB')

	# chop off excess so tiles fit evenly
	width, height = target.size
	width  /= tilesize
	width  *= tilesize
	height /= tilesize
	height *= tilesize

	# output image size fits tiles evenly	
	out_img = Image.new('RGB', (width,height), color=0)

	# sweep over all tile size regions of source image
	for x in range(0, width,tilesize):
		for y in range(0, height,tilesize):
			box = (x, y, x+tilesize, y+tilesize)
			# crop the coordinates of the tile
			region = target.crop(box)
			# find the average RGB value of the tile
			match = best_match(rank_image(region))
			# take match out of availability
			discarded.update({match:tiles[match]})
			del tiles[match]
			match_img = Image.open(source_path+match)
			if match_img.mode is not 'RGBA' or 'RGB': # prevent errors with B&W images
				match_img = match_img.convert('RGB')
			# place tile in appropriate location of our output image
			out_img.paste(match_img, box, None) 


	# save output and show the user
	out_img.save(target_img+"_out.png", "PNG")
	out_img.show()





		
		
		
		




