import math
import datetime
import logging
import logging.handlers as handlers

import extern as ext

import tools.vk_tools as vk_tools


MinutesInDay = 24 * 60


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


def calculate_delay_seconds(min_delay, max_delay, best_minute, minute_of_the_day):

    coeff = 1 - (1 + math.cos(2 * math.pi * (minute_of_the_day - best_minute) / MinutesInDay)) / 2
    if coeff < 0 or coeff > 1:
        ext.logger.error('tools.py: calculate_delay_seconds: invalid coefficient: {}'.format(coeff))
        coeff = 0.5

    return min_delay + coeff * (max_delay - min_delay)


def randomize_delay(delay, percent_cut=ext.PercentCut, percent_add=ext.PercentAdd):
    return delay * (1 - percent_cut) + delay * percent_add


def current_minute():
    now = datetime.datetime.now()
    return now.hour * 60 + now.minute


def current_delay(min_delay=ext.PostDelayMin, max_delay=ext.PostDelayMax, best_minute=ext.MinuteBest):
    minute = current_minute()
    delay = calculate_delay_seconds(min_delay, max_delay, best_minute, minute)
    return randomize_delay(delay)


def print_delays():
    for i in range(MinutesInDay):
        delay = calculate_delay_seconds(20, 60, 19 * 60, i)
        print(delay)
