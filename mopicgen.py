#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A module to create a MO-montage from a .molden file
using JMol and imagemagick."""

import argparse
import logging
logging.basicConfig(level=logging.INFO)
import math
import os.path
import re

from jinja2 import Environment, FileSystemLoader


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
env = Environment(
        loader=FileSystemLoader(os.path.join(THIS_DIR, "templates"))
)


def get_occupations(molden):
    occup_re = "\s*Occup=\s*([-\d\.].+)"
    occups = [float(mo.strip()) for mo in re.findall(occup_re, molden)]
    return occups


def get_symmetries(molden):
    sym_re = "\s*Sym=\s*(.+)"
    syms = [mo.strip() for mo in re.findall(sym_re, molden)]
    # Insert a space after the MO number
    # 40a' will become 40 a'
    syms = [re.sub("(\d+)", r"\1 ", mo) for mo in syms]
    return syms


def get_frac_occ_mos(molden, thresh):
    logging.info("Threshold = {:.4f}".format(thresh))
    logging.info("Considering MOs with occupations between "
                 "{} <= occ <= {}.".format(0+thresh, 2-thresh))
    occups = get_occupations(molden)
    frac_mos = [(mo, occ) for mo, occ in enumerate(occups)
                   if ((0+thresh) <= occ <= (2-thresh))]
    return frac_mos


def save_write(fn, text):
    with open(fn, "w") as handle:
        handle.write(text)


def gen_jmol_input(fn, orient, mos, mos_for_labels_fns, ifx):
    tpl_fn = "jmol.tpl"
    mo_fn_base = "mo_{}{}.png"
    jmol_inp_fn_base = "{}{}.spt"
    # Create 1-based MO indices for Jmol's mo [n] command
    jmol_mos = [mo + 1 for mo in mos]
    if ifx:
        ifx = ".irrep{}".format(ifx)

    tpl = env.get_template(tpl_fn)

    mo_fns = [mo_fn_base.format(mo, ifx) for mo in mos_for_labels_fns]
    rendered = tpl.render(
        fn=fn,
        orient=orient,
        mos_fns=zip(jmol_mos, mo_fns)
    )

    fn_base = os.path.split(fn)[-1]
    jmol_inp_fn = jmol_inp_fn_base.format(fn_base, ifx)
    save_write(jmol_inp_fn, rendered)

    return jmol_inp_fn, mo_fns


def make_input(molden, title, ifx, mos, mos_for_labels_fns, args):
    orient = args.orient

    jmol_inp_fn, mo_fns = gen_jmol_input(fn,
                                         orient,
                                         mos,
                                         mos_for_labels_fns,
                                         ifx
    )

    mo_labels = mos_for_labels_fns
    if args.sym:
        all_sym_label = get_symmetries(molden)
        sym_label = [all_sym_label[mo-1] for mo in mos]
        # Escape potential ' and " characters in the sym labels
        escape_regex = "([\"\'])"
        repl = lambda matchobj: "\\" + matchobj.groups()[0]
        sym_label = [re.sub(escape_regex, repl, mo) for mo in sym_label]
        mo_labels = sym_label
    if args.occ:
        all_occups = get_occupations(molden)
        occups = [all_occups[mo] for mo in mos]
        mo_labels = ["{} ({:.2f})".format(mol, occup)
                     for mol, occup in zip(mos_for_labels_fns, occups)]

    mo_label_list = ['-label "MO {}" {}'.format(mo, mo_fn) for mo, mo_fn in
                     zip(mo_labels, mo_fns)]
    mo_label_str = " ".join(mo_label_list)

    # Prepare montage-string
    montage_tpl = env.get_template("montage_base.tpl")
    montage_str = montage_tpl.render(mo_label_str=mo_label_str,
                                     title=title)

    return jmol_inp_fn, montage_str, ifx


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
    # Optional arguments
    parser.add_argument("--thresh", default=0.0001, type=float,
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

    args = parser.parse_args()
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
        moldens.append(molden)
        is_orca = bool(orca_re.search(molden))

    mos = args.mos

    if args.fracmos:
        args.sym = True
        args.occ = True
        thresh = args.thresh
        mos, frac_occups = zip(*get_frac_occ_mos(molden, thresh))
        logging.warning("Found {:.2f} electrons in {} orbitals.".format(
              sum(frac_occups), len(mos)))

    mos_zero_based = args.fracmos or is_orca

    # Substract 1 from all MO indices when the input is 1-based.
    # 'mos' will be 0-based now.
    if not mos_zero_based:
        mos = [mo - 1 for mo in mos]

    if is_orca:
        logging.info("Found .molden-file generated by ORCA. Expecting"
                     " 0-based MO-input as in ORCA (first MO is MO 0).")
        # Use 'mos' as they are because ORCA MO indices start at 0
        mos_for_labels_fns = mos
    else:
        # Labels are 1-based when we don't have an ORCA log
        mos_for_labels_fns = [mo + 1 for mo in mos]

    to_render = list()
    for molden, title, ifx in zip(moldens, titles, infixe):
        to_render.append(
            make_input(molden, title, ifx, mos, mos_for_labels_fns, args)
        )

    mo_num = len(mos)
    # Determine tiling automatically. Five columns are the default.
    tile = "5x{:g}".format(math.ceil(mo_num / 5))
    tpl_fn = "run.tpl"
    tpl = env.get_template(tpl_fn)
    rendered = tpl.render(to_render=to_render,
                          tile=tile)

    save_write("run.sh", rendered)

    print("Now run:\nbash run.sh")
