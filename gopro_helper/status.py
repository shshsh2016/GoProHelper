
import os
from collections import OrderedDict

from . import api
from . import commands
from .network import get
from .namespace import Struct


def current_mode(info=None):
    """Determine current mode from supplied information.  Return either 'photo' or 'video'.
    This function is way more complicated than necesarry.
    """
    if not info:
        status, settings = commands.get_raw_status_settings()
        info = status

    value = None
    if isinstance(info, Struct):
        try:
            status_mode_id = '43'
            value = info[status_mode_id]
        except KeyError:
            try:
                value = info.mode
            except AttributeError:
                try:
                    value = info.system.mode
                except AttributeError:
                    raise ValueError('unexpected data: {}'.format(info))
    elif isinstance(info, str) or isinstance(info, int):
        value = info

    if value is not None:
        if isinstance(value, str):
            value = value.lower()
            if value == 'video':
                return 'video'
            elif value == 'photo':
                return 'photo'
            else:
                raise ValueError('unexpected mode string value: {}'.format(value))
        elif type(value) == int:
            if value == api._VIDEO_MODE:
                return 'video'
            elif value == api._PHOTO_MODE:
                return 'photo'
            else:
                raise ValueError('unexpected mode integer value: {}'.format(value))

    raise ValueError('unexpected data: {}, {}'.format(info, value))



# def fetch_camera_status():
#     """Fetch basic camera status values
#     """
#     raw_status, raw_settings = commands.get_raw_status_settings()
#     if not raw_status:
#         return
#     # Parse status and settings details
#     # known groups:  ['system', 'storage', 'app', 'wireless', 'broadcast', 'fwupdate', 'liveview', 'setup', 'stream']
#     groups_include = ['system', 'storage', 'app']
#     info = Struct()
#     for group in api.api_details['status']['groups']:
#         # Check for group name in set of to-be-extracted details
#         group_name = group['group'].lower()
#         if group_name in groups_include:
#             for entry in group['fields']:
#                 # Find corresponding entry and value in camera settings output
#                 try:
#                     value = raw_status[    entry['id'] ]
#                 except KeyError:
#                     value = raw_status[str(entry['id'])]
#                 info[entry['name']] = value
#     # Done
#     return info
# def parse_status_values(camera_status):
#     """Extact a few non-retarded bits of information from 'status' group.  Store in flat dict.
#     """
#     # known groups:  ['system', 'storage', 'app', 'wireless', 'broadcast', 'fwupdate', 'liveview', 'setup', 'stream']
#     groups_include = ['system', 'storage', 'app']
#     info = Struct()
#     for group in api.api_details['status']['groups']:
#         # Check for group name in set of to-be-extracted details
#         group_name = group['group'].lower()
#         if group_name in groups_include:
#             for entry in group['fields']:
#                 # Find corresponding entry and value in camera settings output
#                 id_str = str(entry['id'])
#                 value = camera_status[id_str]
#                 info[entry['name']] = value
#     # Done
#     return info
#------------------------------------------------
# # Current status and settings
# def _entry_option_value(entry, index):
#     for option in entry['options']:
#         if option['value'] == index:
#             # Return nice text value
#             return option['display_name']
#     # Fallback to simply returning the index number
#     return str(index)
# def parse_mode_values(camera_settings):
#     """Associate camera numerical setting values with human-readable text.
#     Store in mode-structured dict.
#     """
#     # Main loop over top-level modes
#     info = Struct()
#     modes_include = ['video', 'photo', 'setup']   # 'Multishot', 'Audio', 'Playback', 'Broadcast']
#     for mode in api.api_details['modes']:
#         # Check for mode name in set of to-be-extracted details
#         if mode['display_name'].lower() in modes_include:
#             info_mode = Struct()
#             for entry in mode['settings']:
#                 # Find corresponding entry and value in camera settings output
#                 id_str = str(entry['id'])
#                 index = camera_settings[id_str]
#                 value = _entry_option_value(entry, index)
#                 info_mode[entry['display_name']] = value
#             info[mode['display_name'].lower()] = info_mode
#     # Done
#     return info
# def current_mode():
#     content = get(api.url_status)
#     camera_status = content['status']
#     info_status = parse_status_values(camera_status)
#     if info_status.mode == api._VIDEO_MODE:
#         return 'video'
#     elif info_status.mode == api._PHOTO_MODE:
#         return 'photo'
#     else:
#       raise ValueError(info_status.mode)
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


#------------------------------------------------

if __name__ == '__main__':
    pass

