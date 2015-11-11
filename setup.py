#!/usr/bin/env python3
from distutils.core import setup

setup(name='zscroll',
      version='1.0',
      description='A text scroller for use with panels',
      author='Lit Wakefield',
      author_email='noct[at]openmailbox[dot]org',
      url='https://github.com/noctuid/zscroll',
      license='Simplified BSD',
      # to the bin
      scripts=['zscroll'],
      data_files=[('share/man/man1', ['zscroll.1']),
                  ('share/licenses/zscroll', ['LICENSE']),
                  ('share/zsh/site-functions', ['completion/_zscroll'])
                  ]
      )
