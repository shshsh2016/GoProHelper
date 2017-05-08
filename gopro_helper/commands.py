
from . import api
from . import status


"""
Pre-configured mode URLs:
- url_mode_video
- url_sub_mode_video_video

- url_mode_photo
- url_sub_mode_photo_photo
- url_sub_mode_photo_night
"""


def set_mode_photo():
    resp = api.get(api.url_mode_photo)
    info = status.fetch_camera_info()

    resp = api.get(api.url_sub_mode_photo_photo)
    info = status.fetch_camera_info()

    assert('Photo' in info)

def set_mode_video():
    resp = api.get(api.url_mode_video)
    info = status.fetch_camera_info()

    resp = api.get(api.url_sub_mode_video_video)
    info = status.fetch_camera_info()

    assert('Video' in info)



def shutter_capture():
    resp = api.get(api.url_shutter_capture)


def shutter_stop():
    resp = api.get(api.url_shutter_stop)

