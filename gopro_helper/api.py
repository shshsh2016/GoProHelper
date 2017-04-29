import os
from collections import OrderedDict
import socket
import struct

import requests
import numpy as np
import namespace


base_url = 'http://10.5.5.9/gp/gpControl'

# templates
tpl_setting = base_url + '/setting/{feature:}/{value:}'
tpl_util =    'http://10.5.5.9/gp/{value:}'
tpl_mode =    base_url + '/command/mode?p={mode:}'
tpl_submode = base_url + '/command/sub_mode?mode={mode:}&sub_mode={sub:}'
tpl_file = 'http://10.5.5.9:8080/videos/DCIM/{}/{}'

#------------------------------------------------

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

    # 'default_mode': {'video':     {'feature': 53, 'value': 0},
    #                  'photo':     {'feature': 53, 'value': 1},
    #                  'multishot': {'feature': 53, 'value': 2}},

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

    'looping_interval': {'max':       {'feature': 6, 'value': 0},
                          '5min':     {'feature': 6, 'value': 1},
                         '20min':     {'feature': 6, 'value': 2},
                         '60min':     {'feature': 6, 'value': 3},
                        '120min':     {'feature': 6, 'value': 4}},

    'video_photo_interval': { '5s':   {'feature': 7, 'value': 1},
                             '10s':   {'feature': 7, 'value': 2},
                             '30s':   {'feature': 7, 'value': 3},
                             '60s':   {'feature': 7, 'value': 4}},

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

    'exposure_time': {'auto':         {'feature': 73, 'value': 0},
                      '1/12.5':       {'feature': 73, 'value': 1},
                      '1/15':         {'feature': 73, 'value': 2},
                      '1/24':         {'feature': 73, 'value': 3},
                      '1/25':         {'feature': 73, 'value': 4},
                      '1/30':         {'feature': 73, 'value': 5},
                      '1/48':         {'feature': 73, 'value': 6},
                      '1/50':         {'feature': 73, 'value': 7},
                      '1/60':         {'feature': 73, 'value': 8},
                      '1/80':         {'feature': 73, 'value': 9},
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

    'continuous_rate': {'3':          {'feature': 18, 'value': 0},
                        '5':          {'feature': 18, 'value': 1},
                       '10':          {'feature': 18, 'value': 2}},

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

    'protune_iso_min': {'100':        {'feature': 75, 'value': 3},
                        '200':        {'feature': 75, 'value': 2},
                        '400':        {'feature': 75, 'value': 1},
                        '800':        {'feature': 75, 'value': 0},
                       '1600':        {'feature': 75, 'value': 4}},


    'wdr_image': {'off':              {'feature': 77, 'value': 0},
                  'on':               {'feature': 77, 'value': 1}},

    'raw_image': {'off':              {'feature': 82, 'value': 0},
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


url_analytics = 'http://10.5.5.9/gp/gpControl/analytics/get'


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



#----------------------------------------------------------
#----------------------------------------------------------

# Status
# https://github.com/KonradIT/goprowifihack/blob/master/HERO4/CameraStatus.md
def _status(info):
    results = OrderedDict()

    ###
    # n = 'battery'
    # k = '2'
    # values = {0: 'Very Low',
    #           1: 'Low',
    #           2: 'Half',
    #           3: 'Full',
    #           4: 'Charging'}
    # results[n] = values[info[k]]

    ###
    n = 'processing'
    k = '8'
    results[n] = info[k]

    ###
    n = 'video_duration'
    k = '13'
    results[n] = info[k]

    ###
    n = 'name'
    k = '30'
    results[n] = info[k]

    ###
    n = 'remaining_photos'
    k = '34'
    results[n] = info[k]

    ###
    n = 'remaining_video'
    k = '35'
    results[n] = info[k]

    ###
    n = 'number_videos'
    k = '37'
    results[n] = info[k]

    ###
    n = 'mode'
    k = '43'
    values = {0: 'video',
              1: 'photo',
              2: 'multishot'}
    mode_id = info[k]
    results[n] = values[mode_id]

    ###
    n = 'submode'
    k = '44'
    values = {0: ['Video', 'Single Pic', 'Burst'],
              1: ['TL Video', 'Continuous', 'TimeLapse'],
              2: ['Video+Photo', 'NightPhoto', 'NightLapse']}
    results[n] = values[info[k]][mode_id]

    ###
    n = 'storage'
    k = '54'
    results[n] = info[k]

    ###
    # n = 'GPS'
    # k = '68'
    # results[n] = info[k] == 1

    ###
    n = 'battery_level'
    k = '70'
    results[n] = int(info[k])

    return namespace.Struct(results)


"""
id = {}
id[name] = ID
id[ID] = name

options = {}
options[name] = options
options[options] = name

"""

def _settings(content, feature_id, feature_options):
    results = namespace.Struct()

    for ID, index in content.items():
        ID = int(ID)
        index = int(index)

        try:
            name = feature_id[ID]

            try:
                results[name] = feature_options[name][index]
            except KeyError:
                print('unknown index: {} {} {}'.format(ID, name, index))

        except KeyError:
            # print('unknown ID: {} {}'.format(ID, index))
            pass

    return results



def status_settings(raw=False):
    """Fetch camera status and settings
    """
    content = get(url_status)

    if not content:
        raise ValueError('No response from url: {}'.format(url_status))

    if raw:
        return content
    else:
        results = _status(content['status'])

        if results['mode'] == 'video':
            results_settings = _settings(content['settings'], feature_video_id, feature_video_options)
        elif results['mode'] == 'photo':
            results_settings = _settings(content['settings'], feature_photo_id, feature_photo_options)
        else:
          raise ValueError('eh?')

    results.update(results_settings)

    return results



def get(url, timeout=5):
    try:
        resp = requests.get(url, timeout=timeout)

        if resp.status_code != 200:
            print(resp.reason)
            print(resp.status_code)
            msg = 'Problem making request for: {}'.format(url)

            raise requests.RequestException(msg)
            # content = resp.json()
            # return content

        return resp.json()
    except requests.ConnectTimeout:
        print('timeout')

        return


def gather_timelapse(item, folder_name):
    '''
    Example: {'t': 't', 'n': 'G0097983.JPG', 'g': '9', 'l': '8448', 'mod': '1488021350', 'm': [], 'b': '7983', 's': '104697936
    '''
    name = item['n']
    group = np.int(item['g'])
    begin = np.int(item['b'])
    last = np.int(item['l'])
    time = np.int(item['mod'])

    b, e = os.path.splitext(item['n'])
    # base = np.int([b[1:]])

    name_tpl = 'G{:03d}{{:04d}}' + e
    name_tpl = name_tpl.format(group)

    # Test
    name_first = name_tpl.format(begin)
    if not name == name_first:
        raise ValueError('Unexpected first name: {} != {}'.format(name, name_first))

    # Do it
    res = []
    for k in range(begin, last+1):
        name_k = name_tpl.format(k)
        url = tpl_file.format(folder_name, name_k)

        res_k = {'url': url, 'time': time}

        res.append(res_k)

    return res


def gather_item(item, folder_name):
    name = item['n']
    size = np.int(item['s'])
    time = np.int(item['mod'])

    url = tpl_file.format(folder_name, name)

    res = {'url': url, 'time': time, 'size': size}

    return res



def filelist(details=False):
    resp = get(url_filelist, timeout=30)
    if not resp:
        raise ValueError('No response from url: {}'.format(url_filelist))

    results = []
    for folder in resp['media']:
        folder_name = folder['d']

        if details:
            results.append(folder)
        else:

            for item in folder['fs']:
                kind = item.get('t', None)

                if kind == 't':
                    res = gather_timelapse(item, folder_name)
                    results.extend(res)
                elif kind == 'b':
                    # burst??
                    res = gather_timelapse(item, folder_name)
                    results.extend(res)
                elif kind == None:
                    # # Normal
                    # name = item['n']
                    # size = np.int(item['s'])
                    # time = np.int(item['mod'])

                    # url = tpl_file.format(folder_name, name)

                    # res = {'url': url, 'time': time}
                    res = gather_item(item, folder_name)
                    results.append(res)

                else:
                    raise ValueError('Unexpected kind: {}'.format(kind))


    return results


def download(url):
    '''
    http://stackoverflow.com/questions/13137817/
    how-to-download-image-using-requests/13137873#13137873
    '''
    path_out = os.path.realpath(os.path.curdir)

    chunk_size = 1024*128
    resp = requests.get(url, stream=True)

    if resp.status_code != 200:
        print(resp.headers)
        print(resp.status_code)
        msg = 'Problem making request for: {}'.format(url)

        raise requests.RequestException(msg)

    file_size = resp.headers['content-length']

    print(file_size)

    # Open local file for writing.
    fname = os.path.basename(url)
    f = os.path.join(path_out, fname)
    with open(f, 'wb') as fp:
        for chunk in resp.iter_content(chunk_size):
            fp.write(chunk)

    return fname




IP = '10.5.5.9'
MAC = '5C:E0:C5:09:39:31'

def wake_on_lan(ip=IP, mac=MAC):
    '''Command remote device to turn on.
    '''

    # Check macaddress format and try to compensate.
    if len(mac) == 12:
        pass
    elif len(mac) == 12 + 5:
        sep = mac[2]
        mac = mac.replace(sep, '')
    else:
        raise ValueError('Unexpected MAC address format {}'.format(mac))

    if isinstance(mac, str):
        mac = bytes(mac.encode())

    # Pad the synchronization stream.
    data = b''.join([b'FFFFFFFFFFFF', mac * 20])
    send_data = b''

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = b''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, (ip, 9))


