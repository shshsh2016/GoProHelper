
import os
import requests

from . import json_io


#------------------------------------------------
# Load JSON API information
path_module = os.path.dirname(__file__)
fname_json = os.path.realpath(os.path.join(path_module, 'gpControl-HERO5Black.json'))

api_details = json_io.read(fname_json)

_VIDEO_MODE = 0
_PHOTO_MODE = 1
_MULTI_MODE = 2

#------------------------------------------------

# URL Commands and Settings
base_addr = 'http://10.5.5.9'

# Templates
tpl_setting =  base_addr + '/gp/gpControl/setting/{feature:}/{value:}'
tpl_mode =     base_addr + '/gp/gpControl/command/mode?p={mode:}'
tpl_sub_mode = base_addr + '/gp/gpControl/command/sub_mode?mode={mode:}&sub_mode={sub:}'
tpl_file =     base_addr + ':8080/videos/DCIM/{}/{}'

url_browse =   base_addr + ':8080/videos/DCIM'

#------------------------------------------------
# Simple commands
#
url_status = base_addr + '/gp/gpControl/status'

url_media_list = base_addr + api_details['services']['media_list']['url']

url_shutter_capture  = base_addr + '/gp/gpControl/command/shutter?p=1'
url_shutter_stop =     base_addr + '/gp/gpControl/command/shutter?p=0'

url_delete_all  = base_addr + '/command/storage/delete/all'
url_delete_last = base_addr + '/command/storage/delete/last'

tpl_delete_file = base_addr + '/command/storage/delete/{}'






# Camera modes
# See section 'camera_mode_map' in API json file.
url_mode_video = tpl_mode.format(mode=_VIDEO_MODE)
url_sub_mode_video_video = tpl_sub_mode.format(mode=_VIDEO_MODE, sub=0)

url_mode_photo = tpl_mode.format(mode=_PHOTO_MODE)
url_sub_mode_photo_photo = tpl_sub_mode.format(mode=_PHOTO_MODE, sub=0)
url_sub_mode_photo_night = tpl_sub_mode.format(mode=_PHOTO_MODE, sub=2)

#------------------------------------------------

def get(url, timeout=5):
    """Handy helper to GET information from URL
    """
    try:
        resp = requests.get(url, timeout=timeout)

        if resp.status_code == 200:
            return resp.json()
        else:
            print(resp.reason)
            print(resp.status_code)

            raise requests.RequestException('GET exception: {}'.format(url))

    except requests.ConnectTimeout:
        return
    except OSError:
        return

#------------------------------------------------

if __name__ == '__main__':
    pass
