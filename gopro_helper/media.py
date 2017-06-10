
import os

import bs4

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



def local_data(path_save='./data'):
    """Return list of locally-stored data files
    """
    files = data_io.find(path_save, ['*.JPG', '*.jpg', '*.MP4', '*.mp4'])
    names = [os.path.basename(f) for f in files]

    return names



def update_local_data(path_save='./data', delete=True, show_bar=False):
    """Move any new photos or videos from camera to local storage
    """
    local_names = local_data(path_save)
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


#------------------------------------------------

if __name__ == '__main__':
    pass

