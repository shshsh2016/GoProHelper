
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

    info = status.fetch_camera_info()
    assert('photo' in info)


def set_mode_video():
    resp = get(api.url_mode_video)
    time.sleep(0.05)

    resp = get(api.url_sub_mode_video_video)

    info = status.fetch_camera_info()
    assert('video' in info)


#------------------------------------------------
# Shutter control
def shutter_capture():
    resp = get(api.url_shutter_capture)


def shutter_stop():
    resp = get(api.url_shutter_stop)

#------------------------------------------------
# General settings
def get_status_settings():
    """Fetch current status and settings from camera
    """
    content = get(api.url_status)

    if not content:
        return None, None

    status = Struct(content['status'])
    settings = Struct(content['settings'])

    return status, settings


def set_feature_value(fid, value):
    """Instruct camera to set feature to specified value
    """
    url = api.tpl_setting.format(feature=fid, value=value)
    return get(url)


def get_feature_value(fid, settings=None):
    """Return camera's current value for specified feature ID
    """
    if not settings:
        status, settings = get_status_settings()

    try:
        value = settings[str(fid)]
    except KeyError:
        raise ValueError('Invalid feature ID {}'.format(fid))

    return value


