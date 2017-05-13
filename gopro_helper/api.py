
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
tpl_setting =         base_addr + '/gp/gpControl/setting/{feature:}/{value:}'
tpl_mode =            base_addr + '/gp/gpControl/command/mode?p={mode:}'
tpl_sub_mode =        base_addr + '/gp/gpControl/command/sub_mode?mode={mode:}&sub_mode={sub:}'
tpl_delete_file =     base_addr + '/gp/gpControl/command/storage/delete?p={}'
tpl_file =            base_addr + ':8080/videos/DCIM/{}/{}'

# Simple commands
url_browse =          base_addr + ':8080/videos/DCIM'
url_status =          base_addr + '/gp/gpControl/status'
url_media_list =      base_addr + '/gp/gpMediaList'

url_shutter_capture = base_addr + '/gp/gpControl/command/shutter?p=1'
url_shutter_stop =    base_addr + '/gp/gpControl/command/shutter?p=0'

url_delete_all  =     base_addr + '/gp/gpControl/command/storage/delete/all'
url_delete_last =     base_addr + '/gp/gpControl/command/storage/delete/last'




# Camera modes
# See section 'camera_mode_map' in API json file.
url_mode_video = tpl_mode.format(mode=_VIDEO_MODE)
url_sub_mode_video_video = tpl_sub_mode.format(mode=_VIDEO_MODE, sub=0)

url_mode_photo = tpl_mode.format(mode=_PHOTO_MODE)
url_sub_mode_photo_photo = tpl_sub_mode.format(mode=_PHOTO_MODE, sub=0)
url_sub_mode_photo_night = tpl_sub_mode.format(mode=_PHOTO_MODE, sub=2)

#------------------------------------------------

def get(url, json=True, timeout=5):
    """Handy helper to GET information from URL
    """
    try:
        resp = requests.get(url, timeout=timeout)

        if resp.status_code == 200:
            if json:
                return resp.json()
            else:
                return resp
        else:
            print(resp.reason)
            print(resp.status_code)

            raise requests.RequestException('GET exception: {}'.format(url))

    except requests.ConnectTimeout:
        return
    except OSError:
        return

#------------------------------------------------



# IP = '10.5.5.9'
# MAC = '5C:E0:C5:09:39:31'
# def wake_on_lan(ip=IP, mac=MAC):
#     '''Command remote device to turn on.
#     '''
#     # Check macaddress format and try to compensate.
#     if len(mac) == 12:
#         pass
#     elif len(mac) == 12 + 5:
#         sep = mac[2]
#         mac = mac.replace(sep, '')
#     else:
#         raise ValueError('Unexpected MAC address format {}'.format(mac))
#     if isinstance(mac, str):
#         mac = bytes(mac.encode())
#     # Pad the synchronization stream.
#     data = b''.join([b'FFFFFFFFFFFF', mac * 20])
#     send_data = b''
#     # Split up the hex values and pack.
#     for i in range(0, len(data), 2):
#         send_data = b''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])
#     # Broadcast it to the LAN.
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#     sock.sendto(send_data, (ip, 9))




if __name__ == '__main__':
    pass
