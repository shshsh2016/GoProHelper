

import os

import requests
import numpy as np

from . import api
from .api import get

from .namespace import Struct



def gather_timelapse(item, folder_name):
    '''
    Example: {'t': 't', 'n': 'G0097983.JPG', 'g': '9', 'l': '8448', 'mod': '1488021350', 'm': [], 'b': '7983', 's': '104697936
    '''
    name = item['n']
    group = np.int(item['g'])
    begin = np.int(item['b'])
    last = np.int(item['l'])
    time = np.int(item['mod'])

    b, e = os.path.splitext(item['n'])
    # base = np.int([b[1:]])

    name_tpl = 'G{:03d}{{:04d}}' + e
    name_tpl = name_tpl.format(group)

    # Test
    name_first = name_tpl.format(begin)
    if not name == name_first:
        raise ValueError('Unexpected first name: {} != {}'.format(name, name_first))

    # Do it
    res = []
    for k in range(begin, last+1):
        name_k = name_tpl.format(k)
        url = api.tpl_file.format(folder_name, name_k)

        res_k = {'url': url, 'time': time}

        res.append(res_k)

    return res


def gather_item(item, folder_name):
    name = item['n']
    size = np.int(item['s'])
    time = np.int(item['mod'])

    url = api.tpl_file.format(folder_name, name)

    res = {'url': url, 'time': time, 'size': size}

    return [res]



def get_file_list(details=False):
    resp = get(api.url_filelist, timeout=30)
    if not resp:
        raise ValueError('No response from url: {}'.format(api.url_filelist))

    results = []
    for folder in resp['media']:
        folder_name = folder['d']

        if details:
            results.append(folder)
        else:

            for item in folder['fs']:
                kind = item.get('t', None)

                if kind == 't':
                    # timelapse
                    res = gather_timelapse(item, folder_name)
                elif kind == 'b':
                    # burst
                    res = gather_timelapse(item, folder_name)
                elif kind == None:
                    # normal
                    res = gather_item(item, folder_name)
                else:
                    raise ValueError('Unexpected kind: {}'.format(kind))

                results.extend(res)

    # Done
    return results

#------------------------------------------------

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
    fname = os.path.basename(url)
    f = os.path.join(path_save, fname)

    with open(f, 'wb') as fp:
        for chunk in resp.iter_content(chunk_size):
            fp.write(chunk)

    # Done
    return fname

