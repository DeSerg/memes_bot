import logging
import logging.handlers as handlers

import extern as ext

import tools.files as files


def prepare_log(filepath, log_level=None):

    if log_level is None:
        log_level = logging.DEBUG

    files.create_dir_for_filepath(filepath)
    fh = handlers.TimedRotatingFileHandler(filepath, when='midnight')
    sh = logging.StreamHandler()

    # fh.setFormatter(logging.Formatter(clog.LogFormatNetwork))
    # sh.setFormatter(logging.Formatter(clog.LogFormatNetwork))

    ext.logger.setLevel(log_level)

    ext.logger.addHandler(fh)
    ext.logger.addHandler(sh)


def photo_id(owner_id, album_id, photo_id):
    return '_'.join([owner_id, album_id, photo_id])


def photo_id_from_photo(photo):
    return photo_id(photo.owner_id, photo.album_id, photo.id)
