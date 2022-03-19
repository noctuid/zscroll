#!/usr/bin/env python3
"""Zscroll setup script."""
from distutils.core import setup

setup(
    name='zscroll',
    version='2.0.1',
    description='A text scroller for use with panels',
    author='Fox Kiester',
    author_email='noct[at]posteo[dot]net',
    url='https://github.com/noctuid/zscroll',
    license='GNU General Public License v3 (GPLv3)',
    keywords=["bar", "panel", "text", "scroll", "scroller"],
    # to the bin
    scripts=['zscroll'],
    data_files=[
        ('share/man/man1', ['zscroll.1']),
        ('share/licenses/zscroll', ['LICENSE']),
        ('share/zsh/site-functions', ['completion/_zscroll']),
    ],
)
