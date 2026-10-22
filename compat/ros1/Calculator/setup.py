#!/usr/bin/env python3
"""Expose the shared Python helper through catkin's devel and install spaces."""

from distutils.core import setup

from catkin_pkg.python_setup import generate_distutils_setup

setup(
    **generate_distutils_setup(
        packages=["calculator_legacy"],
        package_dir={"": "src"},
    )
)
