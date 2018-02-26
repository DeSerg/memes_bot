import sys

from modules.db import CDatabaseManager

import extern as ext
import tools.tools as tools


def setup_app():

    tools.prepare_log(ext.LogFilename)

    CDatabaseManager()


def main(argv):

    setup_app()

    try:
        pass
        # vk_tools.load_photos(ext.IdVkGeraId, ext.IdVkMemesAlbum)
        # vk.load_photos(ext.IdVkSerg, ext.IdVkRunCityAlbum)
    except Exception as e:
        ext.logger.error('main: failed to load photos: {}'.format(e))


if __name__ == '__main__':
    main(sys.argv[1:])