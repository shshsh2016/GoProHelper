
import os
from collections import OrderedDict

import requests

from . import api
from .namespace import Struct

from .utility import get



# Status
def _status(info):
    results = OrderedDict()

    ###
    n = 'processing'
    k = '8'
    results[n] = info[k]

    ###
    n = 'video_duration'
    k = '13'
    results[n] = info[k]

    ###
    n = 'name'
    k = '30'
    results[n] = info[k]

    ###
    n = 'remaining_photos'
    k = '34'
    results[n] = info[k]

    ###
    n = 'remaining_video'
    k = '35'
    results[n] = info[k]

    ###
    n = 'number_videos'
    k = '37'
    results[n] = info[k]

    ###
    n = 'mode'
    k = '43'
    values = {0: 'video',
              1: 'photo',
              2: 'multishot'}
    mode_id = info[k]
    results[n] = values[mode_id]

    ###
    n = 'submode'
    k = '44'
    values = {0: ['video', 'single', 'burst'],
              1: ['timelapse video', 'continuous', 'timelapse'],
              2: ['Video+Photo', 'night', 'nightlapse']}
    results[n] = values[info[k]][mode_id]

    ###
    n = 'storage'
    k = '54'
    results[n] = info[k]

    ###
    # n = 'GPS'
    # k = '68'
    # results[n] = info[k] == 1

    ###
    n = 'battery'
    k = '70'
    results[n] = int(info[k])

    return Struct(results)



def _settings(content, feature_id, feature_options):
    results = Struct()

    for ID, index in content.items():
        ID = int(ID)
        index = int(index)

        try:
            name = feature_id[ID]

            try:
                results[name] = feature_options[name][index]
            except KeyError:
                print('unknown index: {} {} {}'.format(ID, name, index))

        except KeyError:
            # print('unknown ID: {} {}'.format(ID, index))
            pass

    return results



def status_settings(raw=False):
    """Fetch camera status and settings
    """
    content = get(api.url_status)

    if not content:
        raise ValueError('No response from url: {}'.format(api.url_status))

    if raw:
        return content
    else:
        results = _status(content['status'])

        if results['mode'] == 'video':
            results_settings = _settings(content['settings'], api.feature_video_id, api.feature_video_options)
        elif results['mode'] == 'photo':
            results_settings = _settings(content['settings'], api.feature_photo_id, api.feature_photo_options)
        else:
          # raise ValueError('multishot not supported')
          print('multishot settings not supported')
          results_settings = {}

    results.update(results_settings)

    return results


def pretty_status():
    """Print pretty status and settings details to console
    """
    tpl = '{:16s}: {}'
    results = status_settings()

    keys = ['name', 'battery', 'gps', 'mode', 'submode', 'resolution', 'white_balance',
            'color', 'ev', 'protune',
            'protune_iso_min', 'protune_iso_max',
            'wdr', 'raw']

    for k in keys:
        print(tpl.format(k, results[k]))

