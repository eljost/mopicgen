load {{ fn }} FILTER "nosort"
mo titleformat ""
frank off
set showhydrogens false;

{{ orient }}

function _setModelState() {

  select;
  Spacefill 0.0;

  frank off;
  font frank 16.0 SansSerif Plain;
  select *;
  set fontScaling false;

}

_setModelState;

background white
mo fill
mo cutoff 0.04

mo nomesh
mo COLOR [0,255,0] [255,255,0]
mo resolution 8

{% for mo, mo_fn in mos_fns %}
mo {{ mo }}
write image pngt "{{ mo_fn }}"
print "Wrote {{ mo_fn }}"
{% endfor %}
