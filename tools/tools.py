import logging
import logging.handlers as handlers

import extern as ext

import tools.vk_tools as vk_tools


def prepare_log(filename, log_level=None):

    if log_level is None:
        log_level = logging.DEBUG

    fh = handlers.TimedRotatingFileHandler(filename, when='midnight')
    sh = logging.StreamHandler()

    # fh.setFormatter(logging.Formatter(clog.LogFormatNetwork))
    # sh.setFormatter(logging.Formatter(clog.LogFormatNetwork))

    ext.logger.setLevel(log_level)

    ext.logger.addHandler(fh)
    ext.logger.addHandler(sh)


def get_photo_id_str(owner_id, album_id, photo_id):
    return '_'.join([owner_id, album_id, photo_id])


def get_photo_id(owner_id, album_id, photo_id):
    owner_id_str = str(owner_id)
    album_id_str = str(album_id)
    photo_id_str = str(photo_id)
    return get_photo_id_str(owner_id_str, album_id_str, photo_id_str)


def get_photo_id_from_photo(photo):
    owner_id = photo.get(vk_tools.KeyPhotoOwnerId)
    album_id = photo.get(vk_tools.KeyPhotoAlbumId)
    photo_id = photo.get(vk_tools.KeyPhotoId)

    if owner_id is None or album_id is None or photo_id is None:
        return None

    return get_photo_id(owner_id, album_id, photo_id)
