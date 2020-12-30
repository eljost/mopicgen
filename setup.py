#!/usr/bin/env python3

from setuptools import setup, find_packages
import sys

if sys.version_info.major < 3:
    raise SystemExit("Python 3 is required!")

setup(
    name="mopicgen",
    version="0.1",
    description="Easily batch-plot orbitals from moldens with Jmol",
    url="https://github.com/eljost/mopicgen",
    maintainer="Johannes Steinmetzer",
    maintainer_email="johannes.steinmetzer@uni-jena.de",
    license="GPL 3",
    platforms=["unix"],
    packages=find_packages(),
    install_requires=[
        "natsort",
        "pyyaml",
        "jinja2",
        "simplejson",
    ],
    entry_points={
        "console_scripts": [
            "mopicgen = mopicgen.main:run_mopicgen",
        ]
    },
)
