from __future__ import division, print_function, unicode_literals, absolute_import

import os

import numpy as np
import requests
import PIL.Image


def read(fp):
    """Read image data from file-like object using PIL.  Return Numpy array.
    """
    with open(fp, 'rb') as fpp:
        img = PIL.Image.open(fpp)
        data = np.asarray(img)

    return data



def write(fp, data, fmt=None, **kwargs):
    """Write image data from Numpy array to file-like object.

    File format is automatically determined from fp if it's a filename, otherwise you
    must specify format via fmt keyword, e.g. fmt = 'png'.

    Parameter options: http://pillow.readthedocs.org/handbook/image-file-formats.html
    """
    img = PIL.Image.fromarray(data)
    img.save(fp, format=fmt, **kwargs)



def download(url, path_save=None):
    """Download file from URL
    """
    if not path_save:
        path_save = os.path.realpath(os.path.curdir)

    chunk_size = 1024*128
    resp = requests.get(url, stream=True)

    if resp.status_code != 200:
        print(resp.headers)
        print(resp.status_code)
        msg = 'Problem making request for: {}'.format(url)

        raise requests.RequestException(msg)

    # file_size = resp.headers['content-length']

    # Open local file for writing
    f = os.path.join(path_save, os.path.basename(url))

    with open(f, 'wb') as fp:
        for chunk in resp.iter_content(chunk_size):
            fp.write(chunk)

    # Done
    return f

#------------------------------------------------

if __name__ == '__main__':
    pass
