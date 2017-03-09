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

Either you supply the MO indices explictly with the `--mos` argument or you use `--fracmos`, which selects all fractionally occupied MOs with occupation numbers in the range (0 + thresh) <= occ <= (2 - thresh). The default threshold is 0.0001. Different values can set with the `--thresh` argument.

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

## Additional arguments
### Occupation numbers and symmetry
The flags `--occ` and `--sym` include information from the *Sym=* and *Occup=* sections of the .molden file into the montage. Both flags are automatically when using the `--fracmos` flag.

### Titles
A custom title for the montage can be supplied with the `--titles` argument. If no title is specified, the .molden-filename will be used. Printing of the title can be supressed with the `--notitle` flag.

### Force 0-based indexing
0-based indexing can be forced with the `--zero` flag.

### Split montage in multiple images
The `--split` argument specifies the maximum number of MOs per montage. Default is 75. If more MOs are requested multiple montages will be created.

### Plot all MOs
Plotting of all MOs can be requested with the `--allmos` flag.
