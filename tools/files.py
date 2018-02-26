import os

import common.extern as cext


def create_dir_for_filepath(filepath):

    try:
        file_dir = os.path.dirname(filepath)

        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        return True
    except OSError as e:
        cext.logger.warning('common: files.py: failed to create directory for filepath {}: exception: {}'.format(filepath, e))
        return False
