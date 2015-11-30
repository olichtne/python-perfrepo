#!/usr/bin/env python2
"""
Install script for python-perfrepo

To install run
    ./setup.py install
"""

__author__ = """
olichtne@redhat.com (Ondrej Lichtner)
"""

from distutils.core import setup

LONG_DESC = """python-perfrepo library
"""

setup(
        name="python-perfrepo",
        version="1",
        url="http://github.com/olichtne/python-perfrepo/",
        license=["GNU GPLv2"],
        author="Ondrej Lichter",
        author_email="olicthe@redhat.com",
        description="PerfRepo Python library and CLI",
        long_description=LONG_DESC,
        platforms=["linux"],
        packages=["perfrepo"],
        scripts=["perfrepo-cli"]
)
