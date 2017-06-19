
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
    # if not settings:
    #     status, settings = get_raw_status_settings()
    try:
        value = settings[str(fid)]
    except KeyError:
        raise ValueError('Invalid feature ID {}'.format(fid))

    return value


def get_raw_status_settings():
    """Fetch current status and settings from camera
    """
    content = get(api.url_status)

    if not content:
        return None, None

    status = Struct(content['status'])
    settings = Struct(content['settings'])

    return status, settings


def get_status():
    """Fetch basic camera status values
    """
    raw_status, raw_settings = get_raw_status_settings()
    if not raw_status:
        return

    # Parse status and settings details
    # known groups:  ['system', 'storage', 'app', 'wireless', 'broadcast', 'fwupdate', 'liveview', 'setup', 'stream']
    groups_include = ['system', 'storage', 'app', 'setup']

    fields_include = [ \
                      'current_time_msec',
                      'mode',
                      'sub_mode',
                      'encoding_active',
                      'system_busy',
                      'system_hot',
                      'battery_level',  # name change
                      'internal_battery_percentage',
                      'gps_status',
                      'remaining_photos',
                      'remaining_video_time',
                      'num_total_photos',
                      'num_total_videos',
                      'remaining_space',
                      'sd_status',
                      ]
                      # 'internal_battery_level',
                      # 'video_selected_flatmode',
                      # 'photo_selected_flatmode',
                      # 'timelapse_selected_flatmode',
                      # 'date_time']

    info = {}
    for group in api.api_details['status']['groups']:
        # Check for group name in set of to-be-extracted details
        group_name = group['group'].lower()
        if group_name in groups_include:
            for entry in group['fields']:
                if entry['name'] in fields_include:
                    # Find corresponding entry and value in camera settings output
                    try:
                        value = raw_status[    entry['id'] ]
                    except KeyError:
                        value = raw_status[str(entry['id'])]

                    info[entry['name']] = value

    name_changes = [['internal_battery_percentage', 'battery_level']]

    for old, new in name_changes:
        value = info.pop(old)
        info[new] = value

    # Move into OrderedDict-based namespace structure
    info_sorted = Struct()
    for k in fields_include:
        if k in info:
            info_sorted[k] = info[k]

    # Done
    return info_sorted


def _find_item_name_by_value(parts, name, value):
    for item in parts:
        if item[name] == value:
            return item

    raise ValueError('item not found: {}'.format(value))


def parse_mode_submode(info_status):
    """Helper function to translate mode/submode numerc value to pretty string values
    """
    info_mode = _find_item_name_by_value(api.api_details['modes'], 'value', info_status.mode)

    info_submode = _find_item_name_by_value(info_mode['settings'], 'path_segment', 'current_sub_mode')

    info_current = _find_item_name_by_value(info_submode['options'], 'value', info_status.sub_mode)

    name_mode = info_mode['display_name']
    name_sub_mode = info_current['display_name']

    return name_mode, name_sub_mode

#------------------------------------------------

if __name__ == '__main__':
    pass
