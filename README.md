# mopicgen
Easily plot MOs from .molden files using python, Jmol and imagemagick.
## Requirements

    python3 / python2 (not tested)
    jinja2
Additionally these commands must be accessible through your $PATH-variable:

    jmol
    mogrify
    montage
## Usage
Call mopicgen.py with one or more .molden files as argument and supply a number of MOs to be plotted. This will create a Jmol-script with the extension .spt and a bash script run.sh with calls to Jmol, mogrify and montage inside.

Either you supply the MO indices explictly with the `--mos` argument or you use `--fracmos`, which selects all fractionally occupied MOs. With open-shell wavefunctions `--fracmos` also selects singly occupied MOs.

Via the `--orient` argument you can supply a custom orientation of your molecule to Jmol. To determine a good orientation just open your .molden file with Jmol, right-click in the main window and select "Show -> Orientation" and copy the last line after the #OR.

A typical call to quickly display an active space from a MOLCAS calculation would be:

    mopicgen.py rasscf.molden --orient "reset;center {6.8806267 9.311521 16.604956}; rotate z -156.69; rotate y 81.16; rotate z 162.16;" --fracmos
    bash run.sh

mopicgen.py can also handle multiple .molden files at the same time. This is especially useful for MOLCAS calculations with symmetry where one has .molden files for every symmetry/irrep. Right now only one set of MO-indices can be specified for all .molden files. So plotting different active spaces with one call to mopicgen.py with `--fracmos` is not supported.

    mopicgen.py rasscf.irrep1.molden rasscf.irrep2.molden --orient "..." --fracmos
    bash run.sh
    
## MO-indexing
Typically MO indices are 1-based, e.g. the first MO has index 1. Not so in ORCA where the first MO has index 0. mopicgen.py detects .molden files from ORCA based on their *[Title]* section which contains "Molden file created by orca_2mkl" and adjusts it's internal indexing. So calling

    mopicgen.py orca.molden.input --mos {0..9}
    bash run.sh
    
would plot the first ten MOs as indexed in ORCA.

For all other .molden files, e.g. from MOLCAS 1-based indexing is assumed. To plot the first ten MOs from a MOLCAS .molden file:

    mopicgen.py molcas.molden --mos {1..10}
    bash run.sh

## Additional information
The flags `--occ` and `--sym` include information from the *Sym=* and *Occup=* sections of the .molden file into the montage. Both flags are automatically when using the `--fracmos` flag.

A custom title for the montage can be supplied with the `--titles` argument. If no title is specified, the .molden-filename will be used. Printing of the title can be supressed with the `--notitle` flag.
