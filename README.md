# mopicgen
Easily plot MOs from .molden files using python, Jmol and imagemagick.
## Requirements

    python3
    jinja2
    simplejson

Additionally these commands have to be accessible through your $PATH-variable:

    jmol
    mogrify
    montage
## Usage
Call *mopicgen.py* with one or more .molden files as argument and supply a number of MOs with `--mos` or use one of the `--fracmos` or `--allmos` flags.

The script will create a Jmol-script (.spt extension) to calculate and plot the MO as well as a bash script (`run.sh`) to call Jmol, mogrify and montage.

Afterwards just call the bash script with `bash run.sh`.

### MO selection
#### Explicit MO selection
Certain MOs can be selected explicitly with the --mos [MO_1] [MO_2] ... [MO_N] argument.
#### Selection of fractionally occupied MOs
Selection of fractionally occupied MOs can be requested with `--fracmos`. All MOs with occupations in the range (0 + thresh) <= occ <= (2 - thresh) will be considered. The default threshold is 0.0001. Different values can be set with the `--thresh` argument.
#### Selection of all MOs
Selection of all MOs can be requested with the `--allmos` flag.

## Molecular orientation
Via the `--orient` argument you can supply a custom orientation to Jmol. To determine a good orientation just open your .molden file with Jmol, right-click in the main window and select "Show -> Orientation" and copy the last line after the #OR. 
### Selection from a menu
Orientations can be saved to a file *orientations.json* in the directory of *mopicgen.py* (JSON-format, `molecule`: `orientation` as key-value-pairs). The menu can be requested with the `--menu` flag.

    {
        "molecule1" : "reset;center {0.21242106 -0.14687419 0.0}; rotate z -144.63; rotate y 67.24; rotate z -170.41;",
        "molecule2" : "reset;center {..}"
        {..}
    }

## MO-indexing
Typically MO indices are 1-based, e.g. the first MO has index 1. Not so in ORCA where the first MO has index 0. mopicgen.py detects .molden files from ORCA based on their *[Title]* section which contains "Molden file created by orca_2mkl" and adjusts it's internal indexing. So calling

    mopicgen.py orca.molden.input --mos {0..9}
    bash run.sh
    
would plot the first ten MOs as indexed in ORCA. 0-based indexing can also be forced with the `--zero` flag.

For all other .molden files, e.g. from MOLCAS 1-based indexing is assumed. To plot the first ten MOs from a MOLCAS .molden file:

    mopicgen.py molcas.molden --mos {1..10}
    bash run.sh

## Plotting MOs from multiple .molden files    
*mopicgen.py* can also handle multiple .molden files at the same time. This is especially useful for MOLCAS calculations with symmetry where one has .molden files for every symmetry/irrep. Right now only one set of MO-indices can be specified for all .molden files. Plotting different active spaces with one call to *mopicgen.py* with `--fracmos` is currently not supported.

    mopicgen.py rasscf.irrep1.molden rasscf.irrep2.molden --orient "..." --fracmos
    bash run.sh

## Custom configuration
Several values like the MO resolution, color of the lobes and the MO cutoff (isovalue) are read from a config file. To customize your configuration just copy it from *templates/config.tpl* next to *mopicgen.py* and rename it to `config.ini`.

    # cd into the directory where mopicgen.py is located
    cp templates/config.tpl config.ini
    
Never modify *templates/config.tpl* directly as it is tracked with git and would result in a merge conflict.

## Additional arguments
### Occupation numbers and symmetry
The flags `--occ` and `--sym` include information from the *Sym=* and *Occup=* sections of the .molden file into the montage. Occupations are automatically used with `--fracmos`.

### Titles
A custom title for the montage can be supplied with the `--titles` argument. If no title is specified, the .molden-filename will be used. Printing of the title can be suppressed with the `--notitle` flag.

### Split montage in multiple images
The `--split` argument specifies the maximum number of MOs per montage (default = 75). If more MOs are requested multiple montages will be created.


## Examples
A typical call to quickly display an active space from a MOLCAS calculation would be:

    mopicgen.py rasscf.molden --orient "reset;center {6.8806267 9.311521 16.604956}; rotate z -156.69; rotate y 81.16; rotate z 162.16;" --fracmos
    bash run.sh
