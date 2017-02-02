#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A module to create a MO-montage from a .molden file
using JMol and imagemagick."""

import argparse
import os.path
import re

from jinja2 import Environment, FileSystemLoader

from qchelper.molden import get_symmetries, get_occupations

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
env = Environment(
        loader=FileSystemLoader(os.path.join(THIS_DIR, "templates"))
)


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
    tpl_fn = "run.tpl"

    mo_label_list = ['-label "MO {}" {}'.format(mo, mo_fn) for mo, mo_fn in
                     zip(mos, mo_fns)]
    mo_label_str = " ".join(mo_label_list)

    tpl = env.get_template(tpl_fn)
    rendered = tpl.render(
        jmol_inp_fn=jmol_inp_fn,
        mo_label_str=mo_label_str,
        title=title,
    )

    return rendered


def make_input(fn, title, ifx, args):
    orient = args.orient
    mos = args.mos

    jmol_inp_fn, mo_fns = gen_jmol_input(fn, orient, mos, ifx)

    with open(fn) as handle:
        molden = handle.read()
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

    return gen_run_script_str(jmol_inp_fn, mo_fns, mo_labels, title)


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

    args = parser.parse_args()
    fns = args.fns
    titles = args.titles
    if not titles:
        titles = [fn for fn in fns]
    if len(fns) is 1:
        infixe = ["", ]
    else:
        infixe = range(1, len(fns)+2)

    run_script_strs = [make_input(fn, title, ifx, args)
                       for fn, title, ifx
                       in zip(fns, titles, infixe)]
    run_script_str = "\n".join(run_script_strs)

    save_write("run.sh", run_script_str)

    print("Now run:\nbash run.sh")
