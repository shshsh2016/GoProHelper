
import os
from collections import OrderedDict

from . import json_io
from . import api

from .namespace import Struct


#------------------------------------------------
# Current status and settings
def entry_option_value(entry, index):
    for option in entry['options']:
        if option['value'] == index:
            # Return nice text value
            return option['display_name']

    # Fallback to simply returning the index number
    return str(index)



def parse_mode_values(camera_settings):
    """Associate camera numerical setting values with human-readable text.
    Store in mode-structured dict.
    """
    # Main loop over top-level modes
    info = Struct()
    modes_include = ['video', 'photo', 'setup']   # 'Multishot', 'Audio', 'Playback', 'Broadcast']

    for mode in api.api_details['modes']:
        # Check for mode name in set of to-be-extracted details
        if mode['display_name'].lower() in modes_include:

            info_mode = Struct()
            for entry in mode['settings']:

                # Find corresponding entry and value in camera settings output
                id_str = str(entry['id'])
                index = camera_settings[id_str]
                value = entry_option_value(entry, index)

                info_mode[entry['display_name']] = value

            info[mode['display_name'].lower()] = info_mode

    # Done
    return info



def parse_status_values(camera_status):
    """Extact a few non-retarded bits of information from 'status' group.  Store in flat dict.
    """
    # known groups:  ['system', 'storage', 'app', 'wireless', 'broadcast', 'fwupdate', 'liveview', 'setup', 'stream']
    groups_include = ['system', 'storage', 'app', 'wireless']

    info = Struct()
    for group in api.api_details['status']['groups']:
        # Check for group name in set of to-be-extracted details
        group_name = group['group']
        if group_name.lower() in groups_include:
            for entry in group['fields']:

                # Find corresponding entry and value in camera settings output
                id_str = str(entry['id'])
                value = camera_status[id_str]

                info[entry['name']] = value

    # Done
    return info


# def _pretty_status(info):
#     # keys = ['system_hot', 'system_busy', 'current_time_msec',
#     #         'internal_battery_percentage', 'remaining_photos', 'remaining_video_time',
#     #         'remaining_space', 'num_total_photos', 'num_total_videos',
#     #         'wifi_bars', 'ap_ssid', 'ap_state', 'app_count']
#     key_pairs = [['internal_battery_percentage', 'Battery'],
#                  ['system_busy', 'Busy'],
#                  ['system_hot', 'Hot'],
#                  ['num_total_photos', 'Photos'],
#                  ['num_total_videos', 'Videos'],
#                  ['remaining_space', 'Space']]
#     info_out = Struct()
#     for k_in, k_out in key_pairs:
#         # k_out = k.replace('_', ' ')
#         # k_out = ' '.join([s.capitalize() for s in k_out.split()])
#         info_out[k_out] = info[k_in]
#     return info_out
# def _pretty_modes(info):
#     # keys = {'Video': ['Color', 'White Balance', 'EV Comp', 'Field of View', 'ISO', 'ISO Mode',
#     #                   'Low Light', 'Frames Per Second', 'Shutter', 'Resolution',
#     #                   'Video Stabilization', 'Sharpness', 'Protune'],
#     #         'Photo': ['Color', 'EV Comp', 'ISO MIN', 'ISO MAX', 'WDR', 'Shutter', 'Megapixels',
#     #                   'RAW', 'Protune', 'White Balance', 'Sharpness'],
#     #         'Setup': ['Current Flat Mode', 'Auto Off', 'GPS']}
#     keys = {'video': [
#                       ['Frames Per Second', 'FPS'],
#                        'Resolution',
#                        'Shutter',
#                        'ISO',
#                        'ISO Mode',
#                        'EV Comp',
#                        'Low Light',
#                       ['White Balance', 'White'],
#                        'Color',
#                        'Protune',
#                        'Sharpness',
#                       ['Field of View', 'FOV'],
#                       ['Video Stabilization', 'Stabilize']],
#             'photo': [ 'Megapixels',
#                        'Shutter',
#                        'ISO MIN',
#                        'ISO MAX',
#                        'EV Comp',
#                        'WDR',
#                       ['White Balance', 'White'],
#                        'Color',
#                        'Protune',
#                        'Sharpness',
#                        'RAW'],
#             'setup': [['Current Flat Mode', 'Mode'], 'Auto Off', 'GPS']}
#     info_out = Struct()
#     for n, g in keys.items():
#         info_out[n] = {}
#         for k in g:
#             if isinstance(k, str):
#                 info_out[n][k] = info[n][k]
#             else:
#                 k_in, k_out = k
#                 info_out[n][k_out] = info[n][k_in]
#     return info_out


def current_mode():
    content = api.get(api.url_status)
    camera_status = content['status']

    info_status = parse_status_values(camera_status)

    if info_status.mode == api._VIDEO_MODE:
        return 'video'
    elif info_status.mode == api._PHOTO_MODE:
        return 'photo'
    else:
      raise ValueError(info_status.mode)


def fetch_camera_info(pretty=False):
    """Fetch status and mode settings information from camera.
    Optionally return as nicely-formatted dict.
    """
    # Fetch info from camera.  Camera status GET returns two objects: 'status' and 'settings'.
    # The 'settings' object includes all 'mode' information.
    content = api.get(api.url_status)

    if not content:
        return

    camera_status = content['status']
    camera_settings = content['settings']

    # Parse status and settings details
    info_status = parse_status_values(camera_status)
    info = parse_mode_values(camera_settings)

    if pretty:
        raise ValueError('no longer supported')
        # info_status = _pretty_status(info_status)
        # info = _pretty_modes(info)

    # Exclude non-current mode info
    if info_status.mode == api._VIDEO_MODE:
        info.mode = 'video'
        info.pop('photo')
    elif info_status.mode == api._PHOTO_MODE:
        info.mode = 'photo'
        info.pop('video')
    else:
        pass

    # Combine
    info['system'] = info_status

    # Done
    return info

#------------------------------------------------

if __name__ == '__main__':
    pass

