#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A module to create a MO-montage from a .molden file
using JMol and imagemagick."""

import argparse
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


def get_frac_occ_mos(molden):
    occups = get_occupations(molden)
    frac_mos = [(mo, occ) for mo, occ in enumerate(occups)
                   if (occ != 0.0) and (occ != 2.0)]
    return frac_mos


def save_write(fn, text):
    with open(fn, "w") as handle:
        handle.write(text)


def gen_jmol_input(fn, orient, mos, ifx):
    tpl_fn = "jmol.tpl"
    mo_fn_base = "mo_{}{}.png"
    jmol_inp_fn_base = "{}{}.spt"
    if ifx:
        ifx = ".irrep{}".format(ifx)

    tpl = env.get_template(tpl_fn)

    mo_fns = [mo_fn_base.format(mo, ifx) for mo in mos]
    rendered = tpl.render(
        fn=fn,
        orient=orient,
        mos_fns=zip(mos, mo_fns)
    )

    fn_base = os.path.split(fn)[-1]
    jmol_inp_fn = jmol_inp_fn_base.format(fn_base, ifx)
    save_write(jmol_inp_fn, rendered)

    return jmol_inp_fn, mo_fns


def gen_run_script_str(jmol_inp_fn, mo_fns, mos, title):

    return rendered


def make_input(molden, title, ifx, args):
    orient = args.orient
    mos = args.mos

    jmol_inp_fn, mo_fns = gen_jmol_input(fn, orient, mos, ifx)

    mo_labels = mos
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
        occups = [all_occups[mo-1] for mo in mos]
        mo_labels = ["{} ({:.2f})".format(mol, occup)
                     for mol, occup in zip(mo_labels, occups)]

    mo_label_list = ['-label "MO {}" {}'.format(mo, mo_fn) for mo, mo_fn in
                     zip(mo_labels, mo_fns)]
    mo_label_str = " ".join(mo_label_list)

    return jmol_inp_fn, mo_label_str, title, ifx


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Prepare an overview of MOs in a "
                                     ".molden file.")
    parser.add_argument("fns", nargs="+", help=".molden file to be read")
    parser.add_argument("--orient", help="Orientation command from Jmol.")
    parser.add_argument("--mos", nargs="+", type=int,
                        help="MOs to be plotted.")
    parser.add_argument("--titles", nargs="+", help="Title of the montage, e.g."
                        " compound name and/or level of theory.")
    parser.add_argument("--sym", help="Read MO label from .molden-file.",
                        action="store_true")
    parser.add_argument("--occ", action="store_true", help="Include MO "
                        "occupations in the MO label.")
    parser.add_argument("--molcas", action="store_true", help="Determine "
                        " active space MOs automatically.")

    args = parser.parse_args()
    fns = args.fns
    titles = args.titles
    if not titles:
        titles = [fn for fn in fns]
    if len(fns) is 1:
        infixe = ["", ]
    else:
        infixe = range(1, len(fns)+2)

    moldens = list()
    for fn in fns:
        with open(fn) as handle:
            molden = handle.read()
        moldens.append(molden)

    if args.molcas:
        args.sym = True
        args.occ = True
        mos, frac_occups = zip(*get_frac_occ_mos(molden))
        # These MO indices are 0-based whereas with manual input
        # the first MO has index 1. So we add 1 to all MO indices
        # to mimic manually inputted MOs.
        mos = [mo+1 for mo in mos]
        args.mos = mos
        print("Found {:.2f} electrons in {} orbitals.".format(
              sum(frac_occups), len(mos)))

    # Substract 1 from all MO indices because python list indices
    # are 0-based and the user input MO-indices are 1-based.
    mos = [mo - 1 for mo in mos]

    to_render = [make_input(molden, title, ifx, args)
                 for molden, title, ifx
                 in zip(moldens, titles, infixe)]

    tpl_fn = "run.tpl"
    tpl = env.get_template(tpl_fn)
    rendered = tpl.render(to_render=to_render)

    save_write("run.sh", rendered)

    print("Now run:\nbash run.sh")
