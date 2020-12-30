#!/bin/bash

# Columns x Rows
tile="5x"


# Start jmol without display
jmol -o -g 1500x1500 -n TODO.spt
# Crop the generated MO pictures
mogrify -verbose -trim +repage mo_*.png

# Create the montages
# PNG with transparent background

montage -verbose -label "MO 100" mo_100.png \
-title "TODO" \
-tile $tile \
-geometry "600x600>" \
-shadow \
-pointsize 60 \
-background none \
montage.0.PNG


# JPG with white background
mogrify -verbose -background white -alpha remove -format jpg montage*.PNG
