
from __future__ import division, print_function, unicode_literals, absolute_import

try:
    import simplejson as json
except ImportError:
    import json


import contextlib
import numpy as np


@contextlib.contextmanager
def file_like(fp, mode='r'):
    """
    Check if supplied fp is a string instead of the aassumed file-like object.  If so, assume
    it's a file name and so open it for reading or writing as indicated by supplied mode keyword.
    """
    opend_it = False
    if isinstance(fp, str):
        try:
            fp = open(fp, mode)
            opend_it = True
        except IOError:
            msg = 'Supplied string could not be opened as a file: {}'.format(fp)
            raise IOError(msg)

    yield fp

    if opend_it:
        fp.close()


def encode_numpy(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        raise TypeError


def read(fp):
    """
    Read JSON-serialized data from file object (or filename), decode into Python object(s).

    Parameters
    ----------
    fp : file-like object or a file name.
    """
    # Decode file data.
    with file_like(fp, 'r') as fp:
        data = json.load(fp)

    # Done.
    return data


def write(fp, data, pretty=True):
    """
    Encode Python object(s), write to JSON file.

    Parameters
    ----------
    fp : file-like object or a file name.
    data : Data to be written to file.  May include Numpy arrays.
    """
    with file_like(fp, 'w') as fp:
        if pretty:
            # Easy to read.
            separators = (', ', ': ')
            json.dump(data, fp, default=encode_numpy, separators=separators,
                      sort_keys=True, indent='  ')
        else:
            # Compact.
            separators = (',', ':')
            json.dump(data, fp, default=encode_numpy, separators=separators,
                      sort_keys=True)

#################################################

if __name__ == '__main__':
    pass
