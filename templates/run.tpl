#!/bin/bash

# Columns x Rows
tile="{{ tile }}"

{% for jmol_inp_fn, montage_str, ifx in to_render %}
# Start jmol without display
jmol -o -g 1500x1500 -n {{ jmol_inp_fn }}
# Crop the generated MO pictures
mogrify -trim +repage mo_*.png

# Create the montages
# PNG with transparent background
{{ montage_str }}
-background none \
montage{{ ifx }}.PNG

# JPG with white background
{{ montage_str }}
-background white \
montageW{{ ifx }}.jpg
{% endfor %}
