
import os
import time

import numpy as np
import requests
import bs4

import data_io
from progress_bar import bar

from . import api
from . import status

from .namespace import Struct


#------------------------------------------------
# Camera modes

def set_mode_photo():
    resp = api.get(api.url_mode_photo)
    time.sleep(0.05)

    resp = api.get(api.url_sub_mode_photo_photo)
    info = status.fetch_camera_info()

    assert('photo' in info)


def set_mode_video():
    resp = api.get(api.url_mode_video)
    time.sleep(0.05)

    resp = api.get(api.url_sub_mode_video_video)
    info = status.fetch_camera_info()

    assert('video' in info)


#------------------------------------------------
# Shutter control
def shutter_capture():
    resp = api.get(api.url_shutter_capture)


def shutter_stop():
    resp = api.get(api.url_shutter_stop)

#------------------------------------------------
# General settings
def get_status_settings():
    """Fetch current status and settings from camera
    """
    content = api.get(api.url_status)

    if not content:
        return

    status = Struct(content['status'])
    settings = Struct(content['settings'])

    return status, settings


def set_feature_value(fid, value):
    """Instruct camera to set feature to specified value
    """
    url = api.tpl_setting.format(feature=fid, value=value)
    return api.get(url)



#################################################
#------------------------------------------------
# Video and photo files
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

                        if '.jpg' in url.lower() or '.mp4' in url.lower():
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

    resp = api.get(url, json=False)

    return resp.ok



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

    try:
        with open(f, 'wb') as fp:
            for chunk in resp.iter_content(chunk_size):
                fp.write(chunk)

    except KeyboardInterrupt:
        os.remove(f)
        raise


    # Done
    return f


def local_data(path_save='./data'):
    """Return list of locally-stored data files
    """
    files = data_io.find(path_save, ['*.JPG', '*.jpg', '*.MP4', '*.mp4'])
    names = [os.path.basename(f) for f in files]

    return names


def update_local_data(path_save='./data', delete=True):
    """Move any new photos or videos from camera to local storage
    """
    local_names = local_data(path_save)
    data_urls = get_data_urls()

    for url in bar(data_urls):
        name = os.path.basename(url)
        if name not in local_names:
            f = download(url, path_save)

        if delete:
            delete_file(url)


#------------------------------------------------

