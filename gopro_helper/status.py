
import os
from collections import OrderedDict

from . import json_io
from . import api
from .api import get


#------------------------------------------------
# Current status and settings
def entry_option_value(entry, index):
    for option in entry['options']:
        if option['value'] == index:
            # Return nice text value
            return option['display_name']

    # Fallback to simply returning the index number
    return str(index)



def parse_mode_values(camera_settings, api_details):
    """Associate camera numerical setting values with human-readable text.
    Store in mode-structured dict.
    """
    # Main loop over top-level modes
    info = OrderedDict()
    modes_include = ['Video', 'Photo', 'Setup']   # 'Multishot', 'Audio', 'Playback', 'Broadcast']
    for mode in api_details['modes']:
        if mode['display_name'] in modes_include:

            info_mode = {}
            for entry in mode['settings']:

                # Find corresponding entry and value in camera settings output
                id_str = str(entry['id'])
                index = camera_settings[id_str]
                value = entry_option_value(entry, index)

                info_mode[entry['display_name']] = value

            info[mode['display_name']] = info_mode

    # Done
    return info



def parse_status_values(camera_status, api_details):
    """Extact a few non-retarded bits of information from 'status' group.  Store in flat dict.
    """
    # known groups:  ['system', 'storage', 'broadcast', 'wireless',
    # 'fwupdate', 'liveview', 'setup', 'stream']
    groups_include = ['system', 'storage', 'app', 'wireless']

    info = {}
    for group in api_details['status']['groups']:
        # Check for group name in set of to-be-extracted details
        group_name = group['group']
        if group_name in groups_include:
            for entry in group['fields']:
                id_str = str(entry['id'])
                value = camera_status[id_str]

                info[entry['name']] = value

    # Done
    return info

def _pretty_status(info):
    keys = ['system_hot', 'system_busy', 'current_time_msec',
            'internal_battery_percentage', 'remaining_photos', 'remaining_video_time',
            'remaining_space', 'num_total_photos', 'num_total_videos',
            'wifi_bars', 'ap_ssid', 'ap_state', 'app_count']

    info_out = {}
    for k in keys:
        k_out = k.replace('_', ' ')
        k_out = ' '.join([s.capitalize() for s in k_out.split()])
        info_out[k_out] = info[k]

    return info_out



def _pretty_modes(info):
    keys = {'Video': ['Color', 'White Balance', 'EV Comp', 'Field of View', 'ISO', 'ISO Mode',
                      'Low Light', 'Frames Per Second', 'Shutter', 'Resolution',
                      'Video Stabilization', 'Sharpness', 'Protune'],
            'Photo': ['Color', 'EV Comp', 'ISO MIN', 'ISO MAX', 'WDR', 'Shutter', 'Megapixels',
                      'RAW', 'Protune', 'White Balance', 'Sharpness'],
            'Setup': ['Current Flat Mode', 'Auto Off', 'GPS']}

    info_out = {}
    for n, g in keys.items():
        info_out[n] = {}
        for k in g:
            info_out[n][k] = info[n][k]

    return info_out



def fetch_camera_info(pretty=True):
    """Fetch status and mode settings information from camera.  Optionally return as nicely-
    formatted dict.
    """
    # Fetch info from camera.  Camera status GET returns two objects: 'status' and 'settings'.
    # The 'settings' object includes all 'mode' information.
    content = get(api.url_status)

    if not content:
        return

    camera_status = content['status']
    camera_settings = content['settings']

    # Parse status and settings details
    info_status = parse_status_values(camera_status, api.api_details)
    info_modes = parse_mode_values(camera_settings, api.api_details)
    mode = info_status['mode']

    if pretty:
        info_status = _pretty_status(info_status)
        info_modes = _pretty_modes(info_modes)

    # Exclude non-current mode info
    if mode == api._VIDEO_MODE:
        info_modes.pop('Photo')
    elif mode == api._PHOTO_MODE:
        info_modes.pop('Video')
    else:
        pass

    # Combine
    info_modes['System'] = info_status

    # Done
    return info_modes

#------------------------------------------------

if __name__ == '__main__':
    pass

