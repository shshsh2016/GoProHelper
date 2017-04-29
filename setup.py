
from __future__ import division, print_function, unicode_literals, absolute_import

import setuptools

"""
PyPi Instructions:
https://packaging.python.org/distributing/#uploading-your-project-to-pypi

twine command-line tool:
https://github.com/pypa/twine
"""

version = '2017.4.29'

dependencies = ['requests', 'wireless', 'numpy', 'pillow']

setuptools.setup(install_requires=dependencies,
                 include_package_data=True,
                 packages=setuptools.find_packages(),
                 # zip_safe=False,

                 name='gopro_helper',
                 description='Simple Python API for getting stuff done with my GoPro Hero5 Black',
                 author='Pierre V. Villeneuve',
                 author_email='pierre.villeneuve@gmail.com',
                 url='https://github.com/Who8MyLunch/GoProHelper',
                 download_url='https://github.com/Who8MyLunch/GoProHelper/archive/{}.tar.gz'.format(version),
                 version=version,
                 keywords=['video', 'photo', 'gopro', 'api'])
