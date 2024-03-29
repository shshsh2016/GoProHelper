
import os

import bs4
import exiftool
import matplotlib.pyplot as pyplot

import data_io
from progress_bar import bar

from . import api
from .network import get, download
from .namespace import Struct


"""Video and photo files
"""

# Bse URL for all media, photos and video.  Not just videos as indicated by path name,
_url_base = api.url_browse.split('/videos')[0]

def _emit_folders(soup):
    """Generator for media folder urls on the camera
    """
    for row in soup.body.table.children:
        if row.name == 'tr':
            try:
                cols = list(row.children)
                if len(cols) == 3:
                    third = cols[2].text
                    if 'DIRECTORY' in third:
                        first = cols[0]
                        href = first.a['href']
                        url = _url_base + href

                        yield url

            except AttributeError:
                pass


def _emit_folder_photos(soup):
    """Generator for media folder urls on the camera
    """
    for row in soup.body.table.children:
        if row.name == 'tr':
            try:
                cols = list(row.children)
                if len(cols) == 3:
                    first = cols[0]
                    if first.name == 'td':
                        href = first.a['href']
                        url = _url_base + href

                        if '.jpg' in url.lower() or '.mp4' in url.lower():
                            yield url

            except AttributeError:
                pass



def get_data_urls():
    """Return list of URLs to all videos and photos currently on the camera
    """
    urls = []

    resp = get(api.url_browse, json=False)
    soup = bs4.BeautifulSoup(resp.text, 'lxml')

    for url_folder in _emit_folders(soup):
        resp_folder = get(url_folder, json=False)
        soup_folder = bs4.BeautifulSoup(resp_folder.text, 'lxml')

        for url_photo in _emit_folder_photos(soup_folder):
            urls.append(url_photo)

    return urls



def delete_file(url_file):
    """Delete file on camera using the same URL one might use to download the file
    """
    parts = url_file.split('/')
    name = '/' + parts[-2] + '/' + parts[-1]
    url = api.tpl_delete_file.format(name)

    resp = get(url, json=False)

    return resp.ok



def local_data_files(path_save='./data'):
    """Return full paths of locally-stored data, sorted by date
    """
    files = data_io.find(path_save, ['*.JPG', '*.jpg', '*.MP4', '*.mp4'])

    return files



def update_local_data(path_save='./data', delete=True, show_bar=False):
    """Move any new photos or videos from camera to local storage
    """
    local_files = local_data_files(path_save)
    local_names = [os.path.basename(f) for f in local_files]

    data_urls = get_data_urls()

    if show_bar:
        it = bar(data_urls)
    else:
        it = data_urls


    for url in it:
        name = os.path.basename(url)
        if name not in local_names:
            f = download(url, path_save)

        if delete:
            delete_file(url)



def _convert_metadata(_meta, full=False):
    """Process metadata generated by exiftool
    """
    meta_full = Struct()
    delim = ':'
    for k, v in _meta.items():
        if delim in k:
            group, name = k.split(delim)
            if not group in meta_full:
                meta_full[group] = Struct()

            meta_full[group][name] = v
        else:
            name = k
            meta_full[name] = v

    if full:
        return meta_full

    # Subset
    keys_file = ['FileSize', 'ColorComponents', 'BitsPerSample']

    keys_exif = ['WhiteBalance', 'ISO', 'FocalLength', 'FNumber',
                 'ExposureTime', 'ExposureCompensation', 'ApertureValue',
                 'GPSAltitude', 'GPSAltitudeRef', 'GPSLatitude', 'GPSLatitudeRef',
                 'GPSLongitude', 'GPSLongitudeRef', 'GainControl', 'Sharpness']

    keys_comp = ['GPSDateTime', 'HyperfocalDistance', 'FOV', 'ShutterSpeed', 'LightValue']

    meta = Struct()

    for k in keys_file:
        try:
            meta[k] = meta_full.File[k]
        except KeyError:
            pass

    for k in keys_exif:
        try:
            meta[k] = meta_full.EXIF[k]
        except KeyError:
            pass

    for k in keys_comp:
        try:
            meta[k] = meta_full.Composite[k]
        except KeyError:
            pass

    # Done
    return meta



def metadata(fname, full=False):
    """Load metadata from image file(s)
    """

    if not isinstance(fname, str) and hasattr(fname, '__iter__'):
        # Batch process multiple files
        with exiftool.ExifTool() as exif:
            _meta = exif.get_metadata_batch(fname)

        return [_convert_metadata(_m, full=full) for _m in _meta]

    else:
        # Single file
        with exiftool.ExifTool() as exif:
            _meta = exif.get_metadata(fname)

        return _convert_metadata(_meta, full=full)

#------------------------------------------------

if __name__ == '__main__':
    pass

