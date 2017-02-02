#!/bin/bash

# Start jmol without display
jmol -n {{ jmol_inp_fn }}
# Crop the generated MO pictures
mogrify -trim +repage mo_*.png
# Create the montage
montage {{ mo_label_str }} -title "{{ title }}" -tile 4x5 -geometry +50+50 \
        -shadow -pointsize 60 -background none montage.PNG

montage {{ mo_label_str }} -title "{{ title }}" -tile 4x5 -geometry +50+50 \
        -shadow -pointsize 60 -background white montageW.jpg
