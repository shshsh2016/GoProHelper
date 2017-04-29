from __future__ import division, print_function, unicode_literals, absolute_import

import numpy as np
import PIL.Image


def read(fp):
    """
    Read image data from file-like object using PIL.  Return Numpy array.
    """
    with open(fp, 'rb') as fpp:
        img = PIL.Image.open(fpp)
        data = np.asarray(img)

    return data



def write(fp, data, fmt=None, **kwargs):
    """
    Write image data from Numpy array to file-like object.

    File format is automatically determined from fp if it's a filename, otherwise you
    must specify format via fmt keyword, e.g. fmt = 'png'.

    Parameter options: http://pillow.readthedocs.org/handbook/image-file-formats.html
    """
    img = PIL.Image.fromarray(data)
    img.save(fp, format=fmt, **kwargs)



#################################################

if __name__ == '__main__':
    pass
