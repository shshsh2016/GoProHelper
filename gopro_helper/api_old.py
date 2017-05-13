
import os

from . import namespace
from . import json_io

base_url = 'http://10.5.5.9/gp/gpControl'

# templates
tpl_setting = base_url + '/setting/{feature:}/{value:}'
tpl_util =    'http://10.5.5.9/gp/{value:}'
tpl_mode =     base_url + '/command/mode?p={mode:}'
tpl_sub_mode = base_url + '/command/sub_mode?mode={mode:}&sub_mode={sub:}'
tpl_file = 'http://10.5.5.9:8080/videos/DCIM/{}/{}'

#------------------------------------------------

path_module = os.path.dirname(__file__)
fname_json = os.path.realpath(os.path.join(path_module, 'gpControl-HERO5Black.json'))

# modes and submodes
modes = {'video':                {'mode': 0},
         'photo':                {'mode': 1},
         'multishot':            {'mode': 2}}

sub_modes = {
    'video': {'video':           {'mode': 0, 'sub': 0},
              'timelapse':       {'mode': 0, 'sub': 1},
              'video_photo':     {'mode': 0, 'sub': 2},
              'looping':         {'mode': 0, 'sub': 3}},

     'photo': {'single':         {'mode': 1, 'sub': 0},
               'continuous':     {'mode': 1, 'sub': 1},
               'night':          {'mode': 1, 'sub': 2}},

     'multishot': {'burst':      {'mode': 2, 'sub': 0},
                   'timelapse':  {'mode': 2, 'sub': 1},
                   'nightlapse': {'mode': 2, 'sub': 2}},
    }

# general settings
general = {
    'gps':    {'off':            {'feature': 83, 'value': 0},
                'on':            {'feature': 83, 'value': 1}},

    'leds': {'off':              {'feature': 91, 'value': 0},
             'front':            {'feature': 91, 'value': 1},
             'on':               {'feature': 91, 'value': 2}},

    'orientation': {'auto':      {'feature': 52, 'value': 0},
                    'up':        {'feature': 52, 'value': 1},
                    'down':      {'feature': 52, 'value': 2}},

    'default_mode': {'video':     {'feature': 53, 'value': 0},
                     'photo':     {'feature': 53, 'value': 1},
                     'multishot': {'feature': 53, 'value': 2}},

    'default_multishot_mode': {'burst':      {'feature': 27, 'value': 0},
                               'timelapse':  {'feature': 27, 'value': 1},
                               'nightlapse': {'feature': 27, 'value': 2}},

    'default_video_mode': {'video':           {'feature': 1, 'value': 0},
                           'timelapse video': {'feature': 1, 'value': 1},
                           'video+photo':     {'feature': 1, 'value': 2},
                           'looping':         {'feature': 1, 'value': 3}},

    'default_photo_mode': {'single':     {'feature': 16, 'value': 0},
                           'continuous': {'feature': 16, 'value': 1},
                           'night':      {'feature': 16, 'value': 2}},

    'quick_capture': {'off':          {'feature': 54, 'value': 0},
                      'on':           {'feature': 54, 'value': 1}},

    # 'beeps': {'off':   {'feature': 56, 'value': 0},
    #           '0.7':   {'feature': 56, 'value': 1},
    #           'full':  {'feature': 56, 'value': 2}},

    'video_format': {'ntsc':          {'feature': 57, 'value': 0},
                     'pal':           {'feature': 57, 'value': 1}},

    'on_screen_display': {'off':      {'feature': 58, 'value': 0},
                          'on':       {'feature': 58, 'value': 1}},

    'auto_off': {'never':             {'feature': 59, 'value': 0},
                 '1m':                {'feature': 59, 'value': 1},
                 '2m':                {'feature': 59, 'value': 2},
                 '3m':                {'feature': 59, 'value': 3},
                 '5m':                {'feature': 59, 'value': 4},
                '15m':                {'feature': 59, 'value': 6},
                '30m':                {'feature': 59, 'value': 7}},

    # 'wireless_mode': {'off':          {'feature': 60, 'value': 0},
    #                   'app':          {'feature': 60, 'value': 1},
    #                   'rc':           {'feature': 60, 'value': 2},
    #                   'smart':        {'feature': 60, 'value': 3},
    #                   'unknown_8':    {'feature': 60, 'value': 8}},
    }

# mode-specific settings
video = {
    'resolution': {'4k':              {'feature': 2, 'value':  1},
                   '4k_superview':    {'feature': 2, 'value':  2},
                   '2.7k':            {'feature': 2, 'value':  4},
                   '2.7k_superview':  {'feature': 2, 'value':  5},
                   '2.7k_4:3':        {'feature': 2, 'value':  6},
                   '1440p':           {'feature': 2, 'value':  7},
                   '1080p_superview': {'feature': 2, 'value':  8},
                   '1080p':           {'feature': 2, 'value':  9},
                   '960p':            {'feature': 2, 'value': 10},
                   '720p_superview':  {'feature': 2, 'value': 11},
                   '720p':            {'feature': 2, 'value': 12},
                   'wvga':            {'feature': 2, 'value': 13}},

    'frame_rate': {'120fps':          {'feature': 3, 'value': 0},
                    '24fps':          {'feature': 3, 'value': 1},
                    '90fps':          {'feature': 3, 'value': 3},
                    '60fps':          {'feature': 3, 'value': 5},
                    '48fps':          {'feature': 3, 'value': 7},
                    '30fps':          {'feature': 3, 'value': 8}},
# FRAME_RATE="3"
#   class FrameRate:
#     FR240="0"
#     FR120="1"
#     FR100="2"
#     FR60="5"
#     FR50="6"
#     FR48="7"
#     FR30="8"
#     FR25="9"
#     FR24="10"


    'field_of_view': {'wide':         {'feature': 4, 'value': 0},
                      'medium':       {'feature': 4, 'value': 1},
                      'narrow':       {'feature': 4, 'value': 2},
                      'superview':    {'feature': 4, 'value': 3},
                      'linear':       {'feature': 4, 'value': 4}},

    'timelapse_interval': {'0.5s':    {'feature': 5, 'value': 0},
                           '1s':      {'feature': 5, 'value': 1},
                           '2s':      {'feature': 5, 'value': 2},
                           '5s':      {'feature': 5, 'value': 3},
                          '10s':      {'feature': 5, 'value': 4},
                          '30s':      {'feature': 5, 'value': 5},
                          '60s':      {'feature': 5, 'value': 6}},

    # 'looping_interval': {'max':       {'feature': 6, 'value': 0},
    #                       '5min':     {'feature': 6, 'value': 1},
    #                      '20min':     {'feature': 6, 'value': 2},
    #                      '60min':     {'feature': 6, 'value': 3},
    #                     '120min':     {'feature': 6, 'value': 4}},

    # 'video_photo_interval': { '5s':   {'feature': 7, 'value': 1},
    #                          '10s':   {'feature': 7, 'value': 2},
    #                          '30s':   {'feature': 7, 'value': 3},
    #                          '60s':   {'feature': 7, 'value': 4}},

    'low_light': {'off':              {'feature': 8, 'value': 0},
                  'on':               {'feature': 8, 'value': 1}},

    'spot_meter': {'off':             {'feature': 9, 'value': 0},
                   'on':              {'feature': 9, 'value': 1}},

    'protune': {'off':                {'feature': 10, 'value': 0},
                'on':                 {'feature': 10, 'value': 1}},

    'white_balance': {  'auto':       {'feature': 11, 'value': 0},
                       '3000k':       {'feature': 11, 'value': 1},
                       '4000k':       {'feature': 11, 'value': 5},
                       '4800k':       {'feature': 11, 'value': 6},
                       '5500k':       {'feature': 11, 'value': 2},
                       '6000k':       {'feature': 11, 'value': 7},
                       '6500k':       {'feature': 11, 'value': 3},
                      'native':       {'feature': 11, 'value': 4}},


    'color': {'gopro':                {'feature': 12, 'value': 0},
               'flat':                {'feature': 12, 'value': 1}},

    'iso':   {'6400':                 {'feature': 13, 'value': 0},
              '1600':                 {'feature': 13, 'value': 1},
               '400':                 {'feature': 13, 'value': 2},
              '3200':                 {'feature': 13, 'value': 3},
               '800':                 {'feature': 13, 'value': 4},
               '200':                 {'feature': 13, 'value': 7},
               '200':                 {'feature': 13, 'value': 8}},


    'sharpness': {'high':             {'feature': 14, 'value': 0},
                  'med':              {'feature': 14, 'value': 1},
                  'low':              {'feature': 14, 'value': 2}},

    'ev': {'+2.0':                    {'feature': 15, 'value': 0},
           '+1.5':                    {'feature': 15, 'value': 1},
           '+1.0':                    {'feature': 15, 'value': 2},
           '+0.5':                    {'feature': 15, 'value': 3},
            '0.0':                    {'feature': 15, 'value': 4},
           '-0.5':                    {'feature': 15, 'value': 5},
           '-1.0':                    {'feature': 15, 'value': 6},
           '-1.5':                    {'feature': 15, 'value': 7},
           '-2.0':                    {'feature': 15, 'value': 8}},

    # 'exposure_time': {'auto':         {'feature': 73, 'value': 0},
    #                   '1/12.5':       {'feature': 73, 'value': 1},
    #                   '1/15':         {'feature': 73, 'value': 2},
    #                   '1/24':         {'feature': 73, 'value': 3},
    #                   '1/25':         {'feature': 73, 'value': 4},
    #                   '1/30':         {'feature': 73, 'value': 5},
    #                   '1/48':         {'feature': 73, 'value': 6},
    #                   '1/50':         {'feature': 73, 'value': 7},
    #                   '1/60':         {'feature': 73, 'value': 8},
    #                   '1/80':         {'feature': 73, 'value': 9},
    #                   '1/90':         {'feature': 73, 'value': 10},
    #                   '1/96':         {'feature': 73, 'value': 11},
    #                   '1/100':        {'feature': 73, 'value': 12},
    #                   '1/120':        {'feature': 73, 'value': 13},
    #                   '1/160':        {'feature': 73, 'value': 14},
    #                   '1/180':        {'feature': 73, 'value': 15},
    #                   '1/192':        {'feature': 73, 'value': 16},
    #                   '1/200':        {'feature': 73, 'value': 17},
    #                   '1/240':        {'feature': 73, 'value': 18},
    #                   '1/320':        {'feature': 73, 'value': 19},
    #                   '1/360':        {'feature': 73, 'value': 20},
    #                   '1/400':        {'feature': 73, 'value': 21},
    #                   '1/480':        {'feature': 73, 'value': 22},
    #                   '1/960':        {'feature': 73, 'value': 23},
    #                   '1/1920':       {'feature': 73, 'value': 24}},


    'protune_iso_mode': {'Max':       {'feature': 74, 'value': 0},
                        'Lock':       {'feature': 74, 'value': 1}},




    'eis': {'off':                    {'feature': 78, 'value': 0},
            'on':                     {'feature': 78, 'value': 1}}
   }


photo = {
    'resolution': {'12mp_wide':       {'feature': 17, 'value':  0},
                    '7mp_wide':       {'feature': 17, 'value':  1},
                    '7mp_med':        {'feature': 17, 'value':  2},
                    '5mp_med':        {'feature': 17, 'value':  3},
                   '12mp_narrow':     {'feature': 17, 'value':  8},
                   '12mp_med':        {'feature': 17, 'value':  9},
                   '12mp_linear':     {'feature': 17, 'value': 10}},

    # 'continuous_rate': {'3':          {'feature': 18, 'value': 0},
    #                     '5':          {'feature': 18, 'value': 1},
    #                    '10':          {'feature': 18, 'value': 2}},

    # 'exposure_time':          {'auto':{'feature': 19, 'value': 0},
    #                              '2s':{'feature': 19, 'value': 1},
    #                              '5s':{'feature': 19, 'value': 2},
    #                             '10s':{'feature': 19, 'value': 3},
    #                             '15s':{'feature': 19, 'value': 4},
    #                             '20s':{'feature': 19, 'value': 5},
    #                             '30s':{'feature': 19, 'value': 6}},

    'spot_meter': {'off':             {'feature': 20, 'value': 0},
                    'on':             {'feature': 20, 'value': 1}},

    'protune': {'off':                {'feature': 21, 'value': 0},
                 'on':                {'feature': 21, 'value': 1}},

    'white_balance': {  'auto':       {'feature': 22, 'value': 0},
                       '3000k':       {'feature': 22, 'value': 1},
                       '4000k':       {'feature': 22, 'value': 5},
                       '4800k':       {'feature': 22, 'value': 6},
                       '5500k':       {'feature': 22, 'value': 2},
                       '6000k':       {'feature': 22, 'value': 7},
                       '6500k':       {'feature': 22, 'value': 3},
                      'native':       {'feature': 22, 'value': 4}},

    'color': {'gopro':                {'feature': 23, 'value': 0},
               'flat':                {'feature': 23, 'value': 1}},

    # 'iso':   {'800':                  {'feature': 24, 'value': 0},
    #           '400':                  {'feature': 24, 'value': 1},
    #           '200':                  {'feature': 24, 'value': 2},
    #           '100':                  {'feature': 24, 'value': 3}},

    'sharpness': {'high':             {'feature': 25, 'value': 0},
                   'med':             {'feature': 25, 'value': 1},
                   'low':             {'feature': 25, 'value': 2}},

    'ev': {'+2.0':                    {'feature': 26, 'value': 0},
           '+1.5':                    {'feature': 26, 'value': 1},
           '+1.0':                    {'feature': 26, 'value': 2},
           '+0.5':                    {'feature': 26, 'value': 3},
            '0.0':                    {'feature': 26, 'value': 4},
           '-0.5':                    {'feature': 26, 'value': 5},
           '-1.0':                    {'feature': 26, 'value': 6},
           '-1.5':                    {'feature': 26, 'value': 7},
           '-2.0':                    {'feature': 26, 'value': 8}},


    'protune_iso_max': {'100':        {'feature': 24, 'value': 3},
                        '200':        {'feature': 24, 'value': 2},
                        '400':        {'feature': 24, 'value': 1},
                        '800':        {'feature': 24, 'value': 0},
                       '1600':        {'feature': 24, 'value': 4}},

    'shutter':       {'auto':         {'feature': 73, 'value':  0},
                      '1/12.5':       {'feature': 73, 'value':  1},
                      '1/15':         {'feature': 73, 'value':  2},
                      '1/24':         {'feature': 73, 'value':  3},
                      '1/25':         {'feature': 73, 'value':  4},
                      '1/30':         {'feature': 73, 'value':  5},
                      '1/48':         {'feature': 73, 'value':  6},
                      '1/50':         {'feature': 73, 'value':  7},
                      '1/60':         {'feature': 73, 'value':  8},
                      '1/80':         {'feature': 73, 'value':  9},
                      '1/90':         {'feature': 73, 'value': 10},
                      '1/96':         {'feature': 73, 'value': 11},
                      '1/100':        {'feature': 73, 'value': 12},
                      '1/120':        {'feature': 73, 'value': 13},
                      '1/160':        {'feature': 73, 'value': 14},
                      '1/180':        {'feature': 73, 'value': 15},
                      '1/192':        {'feature': 73, 'value': 16},
                      '1/200':        {'feature': 73, 'value': 17},
                      '1/240':        {'feature': 73, 'value': 18},
                      '1/320':        {'feature': 73, 'value': 19},
                      '1/360':        {'feature': 73, 'value': 20},
                      '1/400':        {'feature': 73, 'value': 21},
                      '1/480':        {'feature': 73, 'value': 22},
                      '1/960':        {'feature': 73, 'value': 23},
                      '1/1920':       {'feature': 73, 'value': 24}},

    'protune_iso_min': {'100':        {'feature': 75, 'value': 3},
                        '200':        {'feature': 75, 'value': 2},
                        '400':        {'feature': 75, 'value': 1},
                        '800':        {'feature': 75, 'value': 0},
                       '1600':        {'feature': 75, 'value': 4}},


    'wdr':       {'off':              {'feature': 77, 'value': 0},
                  'on':               {'feature': 77, 'value': 1}},

    'raw':       {'off':              {'feature': 82, 'value': 0},
                  'on':               {'feature': 82, 'value': 1}},
    }


utils = {
    'locate': {'on':       {'value': 'command/system/locate?p=1'},
               'off':      {'value': 'command/system/locate?p=0'}},

    # 'shutter': {'press':   {'value': 'command/shutter?p=1'},
    #             'release': {'value': 'command/shutter?p=0'}},

    'stream': {'start':    {'value': 'execute?p1=gpstream&c1=restart'},
                'stop':    {'value': 'execute?p1=gpstream&c1=stop'}},

    'delete': {'all':      {'value': 'command/storage/delete/all'},
              'last':      {'value': 'command/storage/delete/last'}},

    # 'sleep':               {'value': 'command/system/sleep'},
    # 'status':              {'value': 'status'},
    # 'filelist':            {'value': 'gpMediaList'},

     # 'reset': '/command/photo/protune/reset'},
    }

#----------------------------

# utils = namespace.Struct(utils)
photo.update(general)
video.update(general)

photo = namespace.Struct(photo)
video = namespace.Struct(video)
modes = namespace.Struct(modes)

# video.kind = 'video'
# photo.kind = 'photo'

# sub_modes = namespace.Struct(sub_modes)

url_shutter_capture  = 'http://10.5.5.9/gp/gpControl/command/shutter?p=1'
url_shutter_stop = 'http://10.5.5.9/gp/gpControl/command/shutter?p=0'

url_filelist = 'http://10.5.5.9/gp/gpMediaList'
url_status = 'http://10.5.5.9/gp/gpControl/status'


###########################################333333

# API features
feature_photo_id = {}
feature_photo_options = {}

feature_video_id = {}
feature_video_options = {}

for feature_name, values in photo.items():
    # Feature ID number
    keys = list(values.keys())
    ID = values[keys[0]]['feature']
    feature_photo_id[feature_name] = ID
    feature_photo_id[ID] = feature_name

    # Feature options
    entries = {}
    for option_name,v in values.items():
        number = v['value']
        entries[option_name] = number
        entries[number] = option_name

    feature_photo_options[feature_name] = entries
    feature_photo_options[ID] = entries


for feature_name, values in video.items():
    # Feature ID number
    keys = list(values.keys())
    ID = values[keys[0]]['feature']
    feature_video_id[feature_name] = ID
    feature_video_id[ID] = feature_name

    # Feature options
    entries = {}
    for option_name,v in values.items():
        number = v['value']
        entries[option_name] = number
        entries[number] = option_name

    feature_video_options[feature_name] = entries
    feature_video_options[ID] = entries



if __name__ == '__main__':
    pass
