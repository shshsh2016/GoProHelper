
import os
import time

import numpy as np
import requests
import bs4

from . import api
from . import status
# from . import image_io

from .namespace import Struct


"""
Pre-configured mode URLs:
- url_mode_video
- url_sub_mode_video_video

- url_mode_photo
- url_sub_mode_photo_photo
- url_sub_mode_photo_night
"""

#------------------------------------------------
# Camera modes

def set_mode_photo():
    resp = api.get(api.url_mode_photo)
    time.sleep(0.05)

    resp = api.get(api.url_sub_mode_photo_photo)
    info = status.fetch_camera_info()

    assert('Photo' in info)


def set_mode_video():
    resp = api.get(api.url_mode_video)
    time.sleep(0.05)

    resp = api.get(api.url_sub_mode_video_video)
    info = status.fetch_camera_info()

    assert('Video' in info)


#------------------------------------------------
# Shutter

def shutter_capture():
    resp = api.get(api.url_shutter_capture)


def shutter_stop():
    resp = api.get(api.url_shutter_stop)


#------------------------------------------------
# Media

# def _gather_timelapse(item, folder_name):
#     '''
#     Example: {'t': 't',
#               'n': 'G0097983.JPG',
#               'g': '9',
#               'l': '8448',
#               'mod': '1488021350',
#               'm': [],
#               'b': '7983',
#               's': '104697936}
#     '''
#     name = item['n']
#     group = np.int(item['g'])
#     begin = np.int(item['b'])
#     last = np.int(item['l'])
#     time = np.int(item['mod'])
#     b, e = os.path.splitext(item['n'])
#     # base = np.int([b[1:]])
#     name_tpl = 'G{:03d}{{:04d}}' + e
#     name_tpl = name_tpl.format(group)
#     # Test
#     name_first = name_tpl.format(begin)
#     if not name == name_first:
#         raise ValueError('Unexpected first name: {} != {}'.format(name, name_first))
#     # Do it
#     res = []
#     for k in range(begin, last+1):
#         name_k = name_tpl.format(k)
#         fname = folder_name + '/' + name_k
#         url = api.tpl_file.format(folder_name, name_k)
#         res_k = {'url': url, 'time': time, 'fname': fname}
#         res.append(res_k)
#     return res
# def _gather_item(item, folder_name):
#     name = item['n']
#     size = np.int(item['s'])
#     time = np.int(item['mod'])
#     fname = folder_name + '/' + name
#     url = api.tpl_file.format(folder_name, name)
#     res = {'url': url, 'time': time, 'size': size, 'fname': fname}
#     return [res]
# def get_file_list(details=False):
#     resp = api.get(api.url_media_list, timeout=30)
#     if not resp:
#         raise ValueError('No response from url: {}'.format(api.url_media_list))
#     results = []
#     for folder in resp['media']:
#         folder_name = folder['d']
#         if details:
#             results.append(folder)
#         else:
#             for item in folder['fs']:
#                 kind = item.get('t', None)
#                 if kind == 't':
#                     # timelapse
#                     res = _gather_timelapse(item, folder_name)
#                 elif kind == 'b':
#                     # burst
#                     res = _gather_timelapse(item, folder_name)
#                 elif kind == None:
#                     # normal
#                     res = _gather_item(item, folder_name)
#                 else:
#                     raise ValueError('Unexpected kind: {}'.format(kind))
#                 results.extend(res)
#     return results

#------------------------------------------------

_url_base = api.url_browse.split('/videos')[0]

def emit_folders(soup):
    """Generator for media folder urls on the camera
    """
    for row in soup.body.table.children:
        if row.name == 'tr':
            try:
                cols = list(row.children)
                if len(cols) == 3:
                    third = cols[2].text
                    if 'DIRECTORY' in third:
                        first = cols[0]
                        href = first.a['href']
                        url = _url_base + href

                        yield url

            except AttributeError:
                pass


def emit_folder_photos(soup):
    """Generator for media folder urls on the camera
    """
    for row in soup.body.table.children:
        if row.name == 'tr':
            try:
                cols = list(row.children)
                if len(cols) == 3:
                    first = cols[0]
                    if first.name == 'td':
                        href = first.a['href']
                        url = _url_base + href

                        if 'jpg' in url.lower():
                            yield url

            except AttributeError:
                pass


def get_data_urls():
    """Return list of URLs to all videos and photos currently on the camera
    """
    urls = []

    resp = api.get(api.url_browse, json=False)
    soup = bs4.BeautifulSoup(resp.text, 'lxml')

    for url_folder in emit_folders(soup):
        resp_folder = api.get(url_folder, json=False)
        soup_folder = bs4.BeautifulSoup(resp_folder.text, 'lxml')

        for url_photo in emit_folder_photos(soup_folder):
            urls.append(url_photo)

    return urls




def delete_file(url_file):
    parts = url_file.split('/')
    name = '/' + parts[-2] + '/' + parts[-1]
    url = api.tpl_delete_file.format(name)

    resp = api.get(url)


# def delete_all():
#     pass
#
# def delete_last():
#     pass



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

    # Open local file for writing
    f = os.path.join(path_save, os.path.basename(url))
    with open(f, 'wb') as fp:
        for chunk in resp.iter_content(chunk_size):
            fp.write(chunk)

    # Done
    return f

