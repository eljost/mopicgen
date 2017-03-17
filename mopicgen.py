#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A module to create a MO-montage from a .molden file
using JMol and imagemagick."""

import argparse
import configparser
from itertools import groupby
import logging
logging.basicConfig(level=logging.INFO)
import math
from operator import itemgetter
import os.path
import re

from jinja2 import Environment, FileSystemLoader


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ENV = Environment(
        loader=FileSystemLoader(os.path.join(THIS_DIR, "templates"))
)
CONFIG = configparser.ConfigParser()
# Try to load a customized config from THIS_DIR
if not CONFIG.read(os.path.join(THIS_DIR, "config.ini")):
    # Use templates/config.tpl as fallback if no customized
    # config.ini was found.
    CONFIG.read(os.path.join(THIS_DIR, "templates/config.tpl"))


def find_continuous_numbers(numbers):
    """Expects a iterable holding numbers and groups the numbers
    when they are continuous.
    http://stackoverflow.com/questions/215424"""
    min_max = list()
    for key, group in groupby(enumerate(numbers), key=lambda i: i[0]-i[1]):
        as_list = list(map(itemgetter(1), group))
        if len(as_list) > 1:
            to_append = (min(as_list), max(as_list))
        else:
            to_append = (as_list[0], )
        min_max.append(to_append)
    return min_max


def continuous_number_string(continuous_numbers):
    """
    Returns a list holding strings. When the groups hold more than
    one item then strings of the form min...max are returned. When
    there the group has only one member then it is converted to a
    string.
    """
    as_strings = list()
    for group in continuous_numbers:
        if len(group) > 1:
            to_append = ("{}..{}".format(min(group), max(group)))
        else:
            to_append = str(group[0])
        as_strings.append(to_append)
    return as_strings


def thresh_validator(as_string):
    as_float = float(as_string)
    # Allow only values between 0 <= thresh < 1.0
    if not 0 <= as_float < 1:
        raise argparse.ArgumentTypeError(
            "Only values between 0 <= thresh < 1.0 are allowed!"
        )
    return as_float


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    # http://stackoverflow.com/a/312464
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_occupations(molden):
    occup_re = "\s*Occup=\s*([-\d\.].+)"
    occups = [float(mo.strip()) for mo in re.findall(occup_re, molden)]
    return occups


def get_symmetries(molden):
    sym_re = "\s*Sym=\s*(.+)"
    syms = [mo.strip() for mo in re.findall(sym_re, molden)]
    # This handles .molden files lacking the Sym= entries, e.g. when
    # they were generated by Multiwfn.
    if len(syms) is 0:
        return None
    # Insert a space after the MO number
    # 40a' will become 40 a'
    syms = [re.sub("(\d+)", r"\1 ", mo) for mo in syms]
    return syms


def get_frac_occ_mos(molden, thresh):
    logging.info("Threshold = {:.4f}".format(thresh))
    logging.info("Considering MOs with occupations between "
                 "{} <= occ <= {}.".format(0+thresh, 2-thresh))
    occups = get_occupations(molden)
    all_electrons = sum(occups)
    frac_mos = [(mo, occ) for mo, occ in enumerate(occups)
                   if ((0+thresh) <= occ <= (2-thresh))]
    found_electrons = sum([occ for mo, occ in frac_mos])
    if math.isclose(all_electrons, found_electrons):
        logging.info("The .molden file probably holds a UHF-wavefunction "
                     "where most orbitals are singly occupied.")
        logging.info("Dropping MOs that are singly occupied.")
        logging.info("Check the generated MOs carefully!")
        frac_mos = [(mo, occ) for mo, occ in frac_mos
                    if not math.isclose(occ, 1.0)]
    return frac_mos


def save_write(fn, text):
    with open(fn, "w") as handle:
        handle.write(text)


def gen_jmol_spt(fn, orient, mos, mos_for_labels_fns, ifx):
    tpl_fn = "jmol.tpl"
    mo_fn_base = "mo_{}{}.png"
    jmol_inp_fn_base = "{}{}.spt"
    config = CONFIG["Jmol"]
    # Create 1-based MO indices for Jmol's mo [n] command
    jmol_mos = [mo + 1 for mo in mos]
    if ifx:
        ifx = ".job{:0>3}".format(ifx)

    tpl = ENV.get_template(tpl_fn)

    mo_fns = [mo_fn_base.format(mo, ifx) for mo in mos_for_labels_fns]
    rendered = tpl.render(
        fn=fn,
        orient=orient,
        mos_fns=zip(jmol_mos, mo_fns),
        config=config
    )

    fn_base = os.path.split(fn)[-1]
    jmol_inp_fn = jmol_inp_fn_base.format(fn_base, ifx)
    save_write(jmol_inp_fn, rendered)

    return jmol_inp_fn, mo_fns


def make_input(molden_tpl, ifx, mos, mos_for_labels_fns, args):
    orient = args.orient
    molden, molden_fn = molden_tpl

    jmol_inp_fn, mo_fns = gen_jmol_spt(molden_fn,
                                       orient,
                                       mos,
                                       mos_for_labels_fns,
                                       ifx
    )

    mo_labels = mos_for_labels_fns
    symmetries = get_symmetries(molden)
    # Only do this when symmetries are requested and we actually have
    # the Sym= entries in the .molden file.
    if args.sym and symmetries:
        sym_label = [symmetries[mo] for mo in mos]
        # Escape potential ' and " characters in the sym labels
        escape_regex = "([\"\'])"
        repl = lambda matchobj: "\\" + matchobj.groups()[0]
        sym_label = [re.sub(escape_regex, repl, mo) for mo in sym_label]
        # Append symmetry labels to MO labels
        mo_labels = ["{}\\n{}".format(mol, sl) for mol, sl
                     in zip(mo_labels, sym_label)]
    if args.occ:
        all_occups = get_occupations(molden)
        occups = [all_occups[mo] for mo in mos]
        mo_labels = ["{} ({:.2f})".format(mol, occup)
                     for mol, occup in zip(mo_labels, occups)]

    mo_label_list = ['-label "MO {}" {}'.format(mo, mo_fn) for mo, mo_fn in
                     zip(mo_labels, mo_fns)]

    return jmol_inp_fn, mo_label_list


def handle_args(args):
    fns = args.fns
    titles = args.titles
    # Use the .molden-filenames as default titles
    if not titles:
        titles = [fn for fn in fns]
    if args.notitle:
        titles = [None for fn in fns]

    if len(fns) is 1:
        infixe = ["", ]
    else:
        infixe = range(1, len(fns)+2)

    moldens = list()
    is_orca = False
    orca_re = re.compile("Molden file created by orca_2mkl")
    for fn in fns:
        with open(fn) as handle:
            molden = handle.read()
        moldens.append((molden, fn))
        is_orca = bool(orca_re.search(molden))

    if is_orca:
        logging.info("Found .molden-file generated by ORCA.")

    mos = args.mos

    # For now only use the first .molden-file to determine MO indices
    first_molden = moldens[0][0]
    if args.fracmos:
        args.sym = True
        args.occ = True
        thresh = args.thresh
        mos, frac_occups = zip(*get_frac_occ_mos(first_molden, thresh))
        logging.info("Found {:g} electrons in {} orbitals.".format(
              sum(frac_occups), len(mos)))
        mo_ranges = find_continuous_numbers(mos)
        cn_string = continuous_number_string(mo_ranges)
        logging.info("Using 0-based MO indices: " + ", ".join(cn_string))

    mos_zero_based = args.fracmos or is_orca or args.zero

    if args.allmos:
        # Determine number of MOs from the number of occurences
        # of Occup= strings.
        mo_num = len(get_occupations(first_molden))
        if mos_zero_based:
            mos = range(mo_num)
        else:
            mos = range(1, mo_num+1)
        logging.info("Found {} MOs with indices {} - {}.".format(
                                                            mo_num,
                                                            mos[0],
                                                            mos[-1]))
    if args.holu:
        sys.exit("--holu has to be implemented.")

    # Substract 1 from all MO indices when the input is 1-based.
    # 'mos' will be 0-based now.
    if not mos_zero_based:
        mos = [mo - 1 for mo in mos]

    if mos_zero_based and not args.fracmos:
        # Suppress the message when --fracmos is used because then
        # we don't have explicit MO input and the reminder is not needed.
        logging.info(" Expecting 0-based MO-input (first MO is MO 0).")
        # Use 'mos' as they are because MO indices start at 0
        mos_for_labels_fns = mos
    else:
        # Labels are 1-based otherwise
        mos_for_labels_fns = [mo + 1 for mo in mos]

    return titles, infixe, moldens, mos, mos_for_labels_fns


def run(title, infix, molden_tpl, mos, mos_for_labels_fns):
        jmol_inp_fn, mo_label_list = make_input(molden_tpl, infix,
                                                mos, mo_labels, args
        )
        montage_strs = list()
        # Prepare montage-strings
        montage_chunks = [" ".join(c) for c
                          in chunks(mo_label_list, args.split)]
        return jmol_inp_fn, montage_chunks, infix, title


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Prepare an overview of MOs in a "
                                     ".molden file.")
    # Required arguments
    parser.add_argument("fns", nargs="+",
                                help=".molden file(s) to be read")
    mo_inp_group = parser.add_mutually_exclusive_group(required=True)
    mo_inp_group.add_argument("--fracmos", action="store_true",
                              help="Consider all MOs with fractional"
                              "occupation ( 0+thresh <= occ <= 2-thresh), "
                              "e.g. MOs in an active space. Default thresh "
                              "is 0.001. It can be set with the --thresh "
                              "argument.")
    mo_inp_group.add_argument("--mos", nargs="+", type=int,
                              help="MOs to be plotted.")
    mo_inp_group.add_argument("--allmos", action="store_true",
                              help="Selects all MOs in the .molden file.")
    mo_inp_group.add_argument("--holu", type=int,
                              help="Select MOs in the range HOMO-N .. LUMO+N.")
    # Optional arguments
    parser.add_argument("--thresh", default=0.0001, type=thresh_validator,
                        help="Set the threshold for --fracmos "
                        "( 0+thresh <= occ <= 2-thresh).")
    parser.add_argument("--orient", default="",
                        help="Orientation command from Jmol.")
    parser.add_argument("--sym", action="store_true",
                        help="Read MO label from .molden-file.")
    parser.add_argument("--occ", action="store_true",
                        help="Include MO occupations in the MO label.")
    title_inp_group = parser.add_mutually_exclusive_group()
    title_inp_group.add_argument("--titles", nargs="+",
                        help="Title of the montage, e.g. compound name and/or"
                        "level of theory.")
    title_inp_group.add_argument("--notitle", action="store_true",
                        help="Suppress title in the montage.")
    parser.add_argument("--split", type=int, default=75,
                        help="Put at most [SPLIT] MOs in one montage. If the "
                        "number of MOs is bigger than this several montages "
                        "will be constructed.")
    parser.add_argument("--zero", action="store_true",
                        help="Use 0-based MO indexing.")

    args = parser.parse_args()
    titles, infixe, moldens, mos, mo_labels = handle_args(args)

    to_render = [run(title, infix, molden_tpl, mos, mo_labels)
                 for title, infix, molden_tpl 
                 in zip(titles, infixe, moldens)]

    # For now only use 5 columns and let montage determine the number
    # rows automatically
    tile = "5x"
    tpl_fn = "run.tpl"
    tpl = ENV.get_template(tpl_fn)
    rendered = tpl.render(to_render=to_render,
                          tile=tile)

    save_write("run.sh", rendered)

    print("Now run:\nbash run.sh")
