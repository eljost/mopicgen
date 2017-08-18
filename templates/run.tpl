#!/bin/bash

# Columns x Rows
tile="{{ tile }}"

{% for jmol_inp_fn, montage_chunks, ifx, title in to_render %}
# Start jmol without display
jmol -o -g 1500x1500 -n {{ jmol_inp_fn }}
# Crop the generated MO pictures
mogrify -verbose -trim +repage mo_*.png

# Create the montages
# PNG with transparent background
{% for montage_chunk in montage_chunks %}
montage -verbose {{ montage_chunk }} \
{% if title %}-title "{{ title }}" \{% endif %}
-tile $tile \
-geometry "600x600>" \
-shadow \
-pointsize 60 \
-background none \
montage{% if ifx %}.job{{ "{:0>3}".format(ifx) }}{% endif %}.{{ loop.index0 }}.PNG

# JPG with white background
mogrify -verbose -background white -alpha remove -format jpg montage{% if ifx %}.job{{ "{:0>3}".format(ifx) }}{% endif %}.{{ loop.index0 }}.PNG
{% endfor %}

{% if rm %}
rm mo_*.png
{% endif %}
{% endfor %}

