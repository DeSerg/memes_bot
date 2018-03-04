import math
import datetime
import logging
import logging.handlers as handlers

import extern as ext

import tools.vk_tools as vk_tools


DelayCoefficientDistribution = {
    0: 0.2,
    1: 0.5,
    2: 0.7,
    3: 0.9,
    4: 1,
    5: 1,
    6: 0.3,
    7: 0.2,
    8: 0.2,
    9: 0.2,
    10: 0.1,
    11: 0.1,
    12: 0.1,
    13: 0.1,
    14: 0.1,
    15: 0.1,
    16: 0.07,
    17: 0.05,
    18: 0,
    19: 0,
    20: 0,
    21: 0,
    22: 0.05,
    23: 0.1
}

MinutesInHour = 60

HoursInDay = 24
MinutesInDay = HoursInDay * MinutesInHour


def prepare_log(filename, log_level=None):

    if log_level is None:
        log_level = logging.DEBUG

    fh = handlers.TimedRotatingFileHandler(filename, when='midnight')
    sh = logging.StreamHandler()

    fh.setFormatter(logging.Formatter(ext.LogFormat))
    sh.setFormatter(logging.Formatter(ext.LogFormat))

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

    # coeff = 1 - (1 + math.cos(2 * math.pi * (minute_of_the_day - best_minute) / MinutesInDay)) / 2
    hour_of_the_day = minute_of_the_day // MinutesInHour
    coeff = DelayCoefficientDistribution.get(hour_of_the_day)
    if coeff is None or coeff < 0 or coeff > 1:
        ext.logger.error('tools.py: calculate_delay_seconds: invalid coefficient: {}'.format(coeff))
        coeff = 0.2

    return min_delay + coeff * (max_delay - min_delay)


def randomize_delay(delay, percent_cut=ext.PercentCut, percent_add=ext.PercentAdd):
    return delay * (1 - percent_cut) + delay * percent_add


def current_minute():
    now = datetime.datetime.now()
    return now.hour * 60 + now.minute


def current_hour():
    now = datetime.datetime.now()
    return now.hour


def current_delay(min_delay=ext.PostDelayMin, max_delay=ext.PostDelayMax, best_minute=ext.MinuteBest):
    minute = current_minute()
    delay = calculate_delay_seconds(min_delay, max_delay, best_minute, minute)
    return randomize_delay(delay)


def print_delays():
    for i in range(HoursInDay):
        delay = calculate_delay_seconds(ext.PostDelayMin // MinutesInHour, ext.PostDelayMax // MinutesInHour, 19 * 60, i * MinutesInHour)
        print('{}: {}'.format(i, delay))
