
import os

from . import json_io
from .namespace import Struct

#------------------------------------------------
# Load JSON API information
path_module = os.path.dirname(__file__)
fname_json = os.path.realpath(os.path.join(path_module, 'gpControl-HERO5Black.json'))

# Load information from camera's JSON file
api_details = json_io.read(fname_json)

#------------------------------------------------

_VIDEO_MODE = 0
_PHOTO_MODE = 1
_MULTI_MODE = 2

# URL Commands and Settings
base_addr = 'http://10.5.5.9'

# Templates
tpl_setting =     base_addr + '/gp/gpControl/setting/{feature:}/{value:}'
tpl_mode =        base_addr + '/gp/gpControl/command/mode?p={mode:}'
tpl_sub_mode =    base_addr + '/gp/gpControl/command/sub_mode?mode={mode:}&sub_mode={sub:}'
tpl_delete_file = base_addr + '/gp/gpControl/command/storage/delete?p={}'
tpl_file =        base_addr + ':8080/videos/DCIM/{}/{}'

# Simple commands
url_browse =      base_addr + ':8080/videos/DCIM'
url_status =      base_addr + '/gp/gpControl/status'
url_media_list =  base_addr + '/gp/gpMediaList'

url_shutter_capture = base_addr + '/gp/gpControl/command/shutter?p=1'
url_shutter_stop =    base_addr + '/gp/gpControl/command/shutter?p=0'

url_delete_all  =     base_addr + '/gp/gpControl/command/storage/delete/all'
url_delete_last =     base_addr + '/gp/gpControl/command/storage/delete/last'


#------------------------------------------------
# Camera modes
# See section 'camera_mode_map' in API json file.
url_mode_video = tpl_mode.format(mode=_VIDEO_MODE)
url_sub_mode_video_video = tpl_sub_mode.format(mode=_VIDEO_MODE, sub=0)

url_mode_photo = tpl_mode.format(mode=_PHOTO_MODE)
url_sub_mode_photo_photo = tpl_sub_mode.format(mode=_PHOTO_MODE, sub=0)
url_sub_mode_photo_night = tpl_sub_mode.format(mode=_PHOTO_MODE, sub=2)

url_mode_multi_shot = tpl_mode.format(mode=_MULTI_MODE)
url_sub_mode_timelapse_photo = tpl_sub_mode.format(mode=_MULTI_MODE, sub=1)

#################################################
# Status and settings useful subsets
_status_fields = ['current_time_msec',
                  'mode',
                  'sub_mode',
                  'encoding_active',
                  'system_busy',
                  'system_hot',
                  # 'battery_level',
                  'battery_present',
                  'battery_percentage',
                  'gps_status',
                  'num_total_photos',
                  'num_total_videos',
                  'remaining_photos',
                  'remaining_video_time',
                  'remaining_space',
                  'sd_status']


#----------------------------------------
# Useful mode / feature IDs
# Restricted to subset of mode/submode combinations useful for my projects
# Assume Protune is always enabled.
_video_features = [ \
                   # 'current_sub_mode',
                   'fov',
                   'resolution',
                   'fps',
                   'exposure_time',
                   'eis',
                   'protune_iso_mode',
                   'protune_iso',
                   'protune_ev',
                   'low_light',
                   # 'protune',
                   'timelapse_rate',
                   'protune_white_balance',
                   'protune_color',
                   'protune_sharpness',
                 ]

_photo_features = [ \
                   'resolution',
                   # 'exposure_time',
                   'protune_exposure_time',
                   'protune_ev',
                   'protune_iso',
                   'protune_iso_min',
                   # 'protune',
                   'single_wdr',
                   'protune_white_balance',
                   'protune_color',
                   'single_raw',
                   'night_raw',
                   'protune_sharpness',
                  ]

_multi_shot_features = [ \
                        'timelapse_rate',
                        'resolution',
                        'exposure_time',
                        # 'burst_rate',
                        # 'nightlapse_rate',
                        'spot_meter',
                        # 'protune',
                        'protune_white_balance',
                        'protune_color',
                        'protune_sharpness',
                        'protune_ev',
                        'protune_iso_min',
                        'protune_iso',
                        'timelapse_wdr',
                        'timelapse_raw',
                        # 'nightlapse_raw',
                       ]

features = Struct()
features.video = _video_features
features.photo = _photo_features
features.multi_shot = _multi_shot_features

# _feature_id = Struct()
# _feature_id.video = Struct()
# _feature_id.video.FOV =         4
# _feature_id.video.Resolution =  2
# _feature_id.video.FPS =         3
# _feature_id.video.Shutter =    73
# _feature_id.video.Stab =       78
# _feature_id.video.ISO_mode =   74
# _feature_id.video.ISO =        13
# _feature_id.video.EV =         15
# _feature_id.video.Low_light =   8
# _feature_id.video.Protune =    10
# _feature_id.video.White =      11
# _feature_id.video.Color =      12
# _feature_id.video.Sharpness =  14
# _feature_id.photo = Struct()
# _feature_id.photo.Resolution = 17
# _feature_id.photo.Shutter =    97
# _feature_id.photo.EV =         26
# _feature_id.photo.ISO_max =    24
# _feature_id.photo.ISO_min =    75
# _feature_id.photo.Protune =    21
# _feature_id.photo.WDR =        77
# _feature_id.photo.White =      22
# _feature_id.photo.Color =      23
# _feature_id.photo.RAW =        82
# _feature_id.photo.Sharpness =  25
#  19 ? shutter time??

#------------------------------------------------
# Helper functions
def camera_modes():
    """Return list of configured camera modes
    """
    exclude = ['broadcast', 'playback']

    mode_names = []
    for info in api_details['modes']:
        if info['path_segment'] not in exclude:
            mode_names.append(info['path_segment'])

    return mode_names



def mode_features(mode):
    """Return feature details direct from camara JSON file
    """
    for info in api_details['modes']:
        if info['path_segment'] == mode:
            return info['settings']



def feature_options(mode, name_or_id):
    """Return options for given mode and feature (name or ID)
    """
    if isinstance(name_or_id, str):
        identifier = 'path_segment'
    else:
        identifier = 'id'

    for F in mode_features(mode):
        if F[identifier] == name_or_id:
            name = F['path_segment']
            # name = F['display_name']
            fid = F['id']
            options = F['options']

            return name, fid, options

    raise ValueError('Invalid mode/feature combination: "{}", "{}"'.format(mode, name_or_id))



def feature_display_name(mode, name_or_id):
    """Return pretty display name for supplied feature ID or path_segment ugly name
    """
    if isinstance(name_or_id, str):
        identifier = 'path_segment'
    else:
        identifier = 'id'

    for F in mode_features(mode):
        if F[identifier] == name_or_id:
            return F['display_name']



def feature_id_name(mode, fid):
    """Return feature name belonging to supplied ID
    """
    name, fid, options = feature_options(mode, fid)
    return name



def feature_name_id(mode, name):
    """Return feature ID belonging to supplied name
    """
    name, fid, options = feature_options(mode, name)
    return fid

#------------------------------------------------

def parse_status_names(raw_status):
    """Parse raw status values into structure with nice field nmames
    """
    # Parse status and settings details
    # known groups:  ['system', 'storage', 'app', 'wireless', 'broadcast',
    #                 'fwupdate', 'liveview', 'setup', 'stream']
    groups_include = ['system', 'storage', 'app', 'setup']


    info = Struct()
    for group in api_details['status']['groups']:
        # Check for group name in set of to-be-extracted details
        group_name = group['group'].lower()
        if group_name in groups_include:
            for entry in group['fields']:
                # if entry['name'] in fields_include:
                    # Find corresponding entry and value in camera settings output
                try:
                    value = raw_status[    entry['id'] ]
                except KeyError:
                    value = raw_status[str(entry['id'])]

                info[entry['name']] = value


    # Prettier names
    name_changes = [['internal_battery_percentage', 'battery_percentage'],
                    ['internal_battery_present', 'battery_present'],
                    ['internal_battery_level', 'battery_level'],
                    # ['external_battery_present', ''],
                    # ['external_battery_level', '']
                    ]

    for old, new in name_changes:
        value = info.pop(old)
        info[new] = value

    # Done
    return info

#######

def _find_item_name_by_value(parts, name, value):
    """Return item whose field with name has given value
    """
    for item in parts:
        if item[name] == value:
            return item

    raise ValueError('item not found: {}'.format(value))



def parse_mode_sub_mode(info_status):
    """Helper function to translate mode/submode numeric value to pretty string values
    """
    info_mode = _find_item_name_by_value(api_details['modes'], 'value', info_status.mode)

    info_sub_mode = _find_item_name_by_value(info_mode['settings'], 'path_segment', 'current_sub_mode')

    info_current = _find_item_name_by_value(info_sub_mode['options'], 'value', info_status.sub_mode)

    name_mode = info_mode['path_segment']
    name_sub_mode = info_current['display_name']

    return name_mode, name_sub_mode


#------------------------------------------------

if __name__ == '__main__':
    pass
