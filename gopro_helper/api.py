
import os

from . import json_io
from .utility import get


#------------------------------------------------
# Load JSON API information
path_module = os.path.dirname(__file__)
fname_json = os.path.realpath(os.path.join(path_module, 'gpControl-HERO5Black.json'))

api_details = json_io.read(fname_json)

#------------------------------------------------

# URL Commands and Settings
base_addr = 'http://10.5.5.9'

url_status = base_addr + '/gp/gpControl/status'

url_media_list = base_addr + api_details['services']['media_list']['url']


url_shutter_capture  = base_addr + '/gp/gpControl/command/shutter?p=1'
url_shutter_stop = base_addr + '/gp/gpControl/command/shutter?p=0'


# templates
tpl_setting = base_addr + '/gp/gpControl/setting/{feature:}/{value:}'
tpl_util =    'http://10.5.5.9/gp/{value:}'
tpl_mode =     base_addr + '/gp/gpControl/command/mode?p={mode:}'
tpl_sub_mode = base_addr + '/gp/gpControl/command/sub_mode?mode={mode:}&sub_mode={sub:}'
tpl_file = 'http://10.5.5.9:8080/videos/DCIM/{}/{}'


#------------------------------------------------
# Simple commands


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
    info = {}
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
    # known groups:  ['system', 'storage', 'broadcast', 'fwupdate', 'liveview', 'setup', 'stream']
    groups_include = ['system', 'storage', 'app']

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
            'remaining_space', 'remaining_timelapse_time', 'num_total_photos', 'num_total_videos']

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



def get_settings(pretty=True):
    """Fetch status and mode settings information from camera.  Optionally return as nicely-
    formatted dict for useful subset.
    """
    # Fetch info from camera.  Camera status GET returns two objects: 'status' and 'settings' (aka modes).
    content = get(url_status)

    camera_status = content['status']
    camera_settings = content['settings']

    # Parse status and settings details
    info_status = parse_status_values(camera_status, api_details)
    info_modes = parse_mode_values(camera_settings, api_details)
    mode = info_status['mode']

    if pretty:
        info_status = _pretty_status(info_status)
        info_modes = _pretty_modes(info_modes)

    _VIDEO_MODE = 0
    _PHOTO_MODE = 1
    _MULTI_MODE = 2

    # Exclude non-current mode info
    if mode == _VIDEO_MODE:
        info_modes.pop('Photo')
    elif mode == _PHOTO_MODE:
        info_modes.pop('Video')
    else:
        pass

    # Combine
    info_modes['System'] = info_status

    # Done
    return info_modes






if __name__ == '__main__':
    pass
