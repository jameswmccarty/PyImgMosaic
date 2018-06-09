#!/usr/bin/python

# This utility reproduces an image from many other
# smaller image 'tiles.'

from PIL import Image
import os
import sys
from subprocess import call
from math import sqrt
from random import randint

""" Create a directory called 'img_src' in the same
location as this script.  Populate this directory with
images that you want to use as small tiles. """

""" Invoke this program with up to four command line arguments:
	1) (mandatory) -f The image file to reproduce.
	2) (mandatory) -s The size of tile to use in the reproduction
	3) (optional) -e An error threshold, that when exceed, adds previously
	   used tiles back into the mix of available tiles.
	4) (optional) -r A percentage of tiles to place cover randomly (not grid aligned)

Example: python PyImgMoasic.py -f moon.jpg -s 16 -r 15

Output is written to filename_out.png, i.e. 
 moon_out.png.

"""

target_img = None
tiles = {} # key is filename, value is avg RGB
discarded = {} # store for used images
tilesize = None
threshold = 66 # determined by experimenting
source_path = "./img_scaled/"
rnd_cover = 20

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
# https://en.wikipedia.org/wiki/Color_difference
def pxl_dist(a, b):
	delt_r = a[0]-b[0]
	delt_bsq = (a[2]-b[2])**2 
	r_bar  = delt_r / 2.
	ssd  = 2 * delt_r**2
	ssd += 4 * (a[1]-b[1])**2
	ssd += 3 * delt_bsq
	ssd += (r_bar * (delt_r**2 - delt_bsq)) / 256.
	return sqrt(ssd)

# find closest match remaining in the dictionary.  give up if no good matches.
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
		print("Tripped error threshold: " + str(err))
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
		print("Threshold set to: " + str(threshold))
		print("Current error is: " + str(err))
		print("RGB value to match was: " + str(val))
		exit()
	return match

def print_usage():
		print("Usage: python PyImgMoasic.py -f filename -s tilesize [-e error] [-r random_placement]")
		print("Example: python PyImgMoasic.py -f moon.jpg -s 16")
		print("Default value for error is " + str(threshold) + ".")
		print("Try smaller error for Black & White input images.")
		print("Default value for random placement is " + str(rnd_cover) + ".")
		exit()

if __name__ == "__main__":

	if len(sys.argv) < 5 or '-f' not in sys.argv or '-s' not in sys.argv:
		print_usage() # show proper format and exit

	# Read user set parameters, and update source path
	target_img = sys.argv[sys.argv.index('-f') + 1]
	tilesize = int(sys.argv[sys.argv.index('-s') + 1])
	if '-e' in sys.argv:
		threshold = int(sys.argv[sys.argv.index('-e') + 1])
	if '-r' in sys.argv:
		rnd_cover = int(sys.argv[sys.argv.index('-r') + 1]) % 100
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

	# cover rnd_cover percent of the image with tiles not aligned to grid
	for r in range(int(width*height*rnd_cover/100./tilesize**2)):
		x = randint(1,width-tilesize-1)
		y = randint(1,height-tilesize-1)
		if x % tilesize == 0:
			x+=1
		if y % tilesize == 0:
			y+=1
		box = (x, y, x+tilesize, y+tilesize)
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
