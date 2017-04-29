#!/usr/bin/python

"""
Great idea from kennethreitz.org for allowing module to import the package.
"""

import os
import sys

# path_work = os.path.abspath(os.path.join('..', '..'))
path_work = os.path.abspath('..')
sys.path.insert(0, path_work)
