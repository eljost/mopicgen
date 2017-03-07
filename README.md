# mopicgen
Easily plot MOs from .molden files using python3, Jmol and imagemagick.
## Requirements

    python3
    jinja2
Additionally these commands must be accessible through your $PATH-variable:

    jmol
    mogrify
    montage
## Usage
Call mopicgen.py with one or more .molden files as argument and supply a number of MOs to be plotted. Either you supply the MO indices explictly with the --mos argument or you use --fracmos, which selects all fractionally occupied MOs. With open-shell wavefunctions --fracmos also select singly occupied MOs.
Via the --orient argument you can supply a custom orientation of your molecule to Jmol. The best orientation can be determined with Jmol.Just open your .molden file with Jmol, right-click in the window and select "Show -> Orientation" and copy the last line after the #OR.

A typical call to quickly display an active space from a MOLCAS calculation would be:

    mopicgen.py rasscf.molden --orient "reset;center {6.8806267 9.311521 16.604956}; rotate z -156.69; rotate y 81.16; rotate z 162.16;" --fracmos
    bash run.sh
    
## MO-indexing
Typically MO indices are 1-based, e.g. the first MO has index 1. Not so in ORCA where the first MO has index 0.mopicgen.py should recognize .molden file from ORCA automatically and adjusts it's internal indexing. So calling

    mopicgen.py orca.molden.input --mos {0..9}
    bash run.sh
    
would plot the first ten MOs as indexed in ORCA. For other .molden files, e.g. from MOLCAS 1-based indexing is assumed so to plot the first ten MOs from a MOLCAS .molden file:

    mopicgen.py molcas.molden --mos {1..10}
    

