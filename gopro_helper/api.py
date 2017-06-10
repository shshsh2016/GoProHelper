
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

#------------------------------------------------

#----------------------------------------
# Camera feature IDs
_feature_id = Struct()

_feature_id.video = Struct()
_feature_id.video.FOV =         4
_feature_id.video.Resolution =  2
_feature_id.video.FPS =         3
_feature_id.video.Shutter =    73
_feature_id.video.Stab =       78
_feature_id.video.EV =         15
_feature_id.video.ISO =        13
_feature_id.video.ISO_mode =   74
_feature_id.video.Low_light =   8
_feature_id.video.Protune =    10
_feature_id.video.White =      11
_feature_id.video.Color =      12
_feature_id.video.Sharpness =  14

_feature_id.photo = Struct()
_feature_id.photo.Resolution = 17
_feature_id.photo.Shutter =    97
_feature_id.photo.EV =         26
_feature_id.photo.ISO_min =    75
_feature_id.photo.ISO_max =    24
_feature_id.photo.Protune =    21
_feature_id.photo.WDR =        77
_feature_id.photo.White =      22
_feature_id.photo.Color =      23
_feature_id.photo.RAW =        82


#------------------------------------------------
# Helper functions
def _mode_details(mode):
    """Return feature details direct from camara JSON file
    """
    for info in api_details['modes']:
        if info['path_segment'] == mode:
            return info['settings']


def video_mode_details():
    return _mode_details('video')


def photo_mode_details():
    return _mode_details('photo')


def feature_id_mode(fid):
    """Determine mode to which specified feature ID belongs: 'photo' or 'video'
    """
    mode = None
    for m in ['photo', 'video']:
        for item in _mode_details(m):
            if item['id'] == fid:
                if not mode:
                    mode = m
                else:
                    raise ValueError('Found multiple entries for feature: {}'.format(fid))

    return mode



def feature_id_name(mode, fid):
    """Return feature name belonging to supplied ID
    """
    for name_k, fid_k in _feature_id[mode]:
        if fid == fid_k:
            return name_k


def feature_choices(mode, fid):
    """Given mode and feature ID, return feature name and key-value pairs of available choices
    """
    details = _mode_details(mode)

    options = Struct()
    for item in details:
        if item['id'] == fid:
            feature_name = item['display_name']
            for entry in item['options']:
                options[entry['display_name']] = entry['value']

            return feature_name, options


#------------------------------------------------

if __name__ == '__main__':
    pass
