#!/bin/bash

# Columns x Rows
tile="4x5"

{% for jmol_inp_fn, mo_label_str, title, ifx in to_render %}
# Start jmol without display
jmol -n {{ jmol_inp_fn }}
# Crop the generated MO pictures
mogrify -trim +repage mo_*.png
# Create the montage
montage {{ mo_label_str }} -title "{{ title }}" -tile $tile -geometry +50+50 \
        -shadow -pointsize 60 -background none montage{{ ifx }}.PNG

montage {{ mo_label_str }} -title "{{ title }}" -tile $tile -geometry +50+50 \
        -shadow -pointsize 60 -background white montageW{{ ifx }}.jpg
{% endfor %}
