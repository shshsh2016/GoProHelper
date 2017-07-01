
import os
import time

import numpy as np
import requests
import bs4

import data_io
from progress_bar import bar

from . import api
from .network import get, download
from .namespace import Struct


#------------------------------------------------
# Camera modes

def set_mode_photo():
    resp = get(api.url_mode_photo)
    time.sleep(0.05)

    resp = get(api.url_sub_mode_photo_photo)


def set_mode_video():
    resp = get(api.url_mode_video)
    time.sleep(0.05)

    resp = get(api.url_sub_mode_video_video)


#------------------------------------------------
# Shutter control
def shutter_capture():
    resp = get(api.url_shutter_capture)


def shutter_stop():
    resp = get(api.url_shutter_stop)

#------------------------------------------------
# General settings
def set_feature_value(fid, value):
    """Instruct camera to set feature to specified value
    """
    url = api.tpl_setting.format(feature=fid, value=value)
    return get(url, json=False)


def get_feature_value(fid, settings):
    """Return camera's current value for specified feature ID.
    """
    try:
        value = settings[str(fid)]
    except KeyError:
        raise ValueError('Invalid feature ID {}'.format(fid))

    return value

#------------------------------------------------


def _keys_str_to_int(D):
    """Status and settings information as returned from camera  uses numbers in string
    form as 'keys'.  I don't like that. Convert strings to integers.
    """
    keys = list(D.keys())
    for k in keys:
        if isinstance(k, str):
            v = D.pop(k)
            D[int(k)] = v

    return D

def get_raw_status_settings():
    """Fetch current raw status and settings from camera
    """
    content = get(api.url_status)

    if not content:
        return None, None

    raw_status = Struct(content['status'])
    raw_settings = Struct(content['settings'])

    raw_status = _keys_str_to_int(raw_status)
    raw_settings = _keys_str_to_int(raw_settings)

    # Process to prettier text names instead of number IDs
    # info_status = api.parse_status(raw_status)

    return raw_status, raw_settings



#------------------------------------------------

if __name__ == '__main__':
    pass
