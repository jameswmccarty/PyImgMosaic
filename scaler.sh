#!/bin/bash

# requires ImageMagic tool 'convert' to be installed
# usage tips from: https://www.imagemagick.org/Usage/resize/

if [[ $# -eq 0 ]] ; then
    echo "Error: Supply resolution of tile size to generate."
	echo "Example: ./scaler.sh 16"
    exit 1
fi

t_size=$1 #tiles will be t_size * t_size pixels

mkdir -p ./img_scaled/${t_size} # unique output directory for each scale
for img in ./img_src/*; do
	[ -e "$img" ] || continue   # make sure globbed file exists
	fname=$(basename "$img")
	[ -e "./img_scaled/${t_size}/${fname}.png" ] && continue # don't create dupes
	echo "Resizing: $fname"
	convert "$img" -resize ${t_size}x${t_size}^ \
		-gravity center -extent ${t_size}x${t_size} "./img_scaled/${t_size}/${fname}.png"
done
