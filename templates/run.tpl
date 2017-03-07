#!/bin/bash

# Columns x Rows
tile="{{ tile }}"

{% for jmol_inp_fn, mo_label_str, title, ifx in to_render %}
# Start jmol without display
jmol -o -g 1000x1000 -n {{ jmol_inp_fn }}
# Crop the generated MO pictures
mogrify -trim +repage mo_*.png
# Create the montage
montage {{ mo_label_str }} -title "{{ title }}" -tile $tile -geometry +50+50 \
        -shadow -pointsize 60 -background none montage{{ ifx }}.PNG

montage {{ mo_label_str }} -title "{{ title }}" -tile $tile -geometry +50+50 \
        -shadow -pointsize 60 -background white montageW{{ ifx }}.jpg
{% endfor %}
