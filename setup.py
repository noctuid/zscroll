#!/usr/bin/env python3
from distutils.core import setup

setup(name='zscroll',
      version='1.0',
      description='A text scroller for use with panels',
      author='Fox Kiester',
      author_email='noct[at]posteo[dot]net',
      url='https://github.com/noctuid/zscroll',
      license='Simplified BSD',
      # to the bin
      scripts=['zscroll'],
      data_files=[('share/man/man1', ['zscroll.1']),
                  ('share/licenses/zscroll', ['LICENSE']),
                  ('share/zsh/site-functions', ['completion/_zscroll'])
                  ]
      )
