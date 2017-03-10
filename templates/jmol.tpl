load {{ fn }} FILTER "nosort"
mo titleformat ""
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
mo cutoff {{ config.Cutoff }}

mo nomesh
mo COLOR {{ config.ColorNegative }} {{ config.ColorPositive }}
mo resolution {{ config.Resolution}}

{% for mo, mo_fn in mos_fns %}
mo {{ mo }}
write image pngt "{{ mo_fn }}"
print "Wrote {{ mo_fn }}"
{% endfor %}
