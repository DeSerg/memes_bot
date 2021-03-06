from PyQt5.QtCore import QCoreApplication

import sys
import os

from modules.db import CDatabaseManager

from bot.bot import CMemesBot

import extern as ext
import tools.tools as tools
import tools.credentials as credentials


ArgTest = 'test'


def create_initial_directories():
    # create vader app dir
    try:
        if not os.path.isdir(ext.LogPath):
            os.makedirs(ext.LogPath)

    except OSError as e:
        print('memes_bot_app.py: create_initial_directories: failed to create initial directories: exception {}'.format(e))


def setup_app(database_filename, argv):
    create_initial_directories()

    ext.App = QCoreApplication(argv)

    tools.prepare_log(ext.LogFilepath)

    CDatabaseManager(database_filename)

    ext.logger.info('Started')


def main(argv):

    bot_token = credentials.MemesBotToken
    channel_id = ext.MemesChannelId
    database_filename = ext.DatabaseFilename
    test_mode = False

    if len(argv) > 0 and argv[0] == ArgTest:
        test_mode = True
        bot_token = credentials.MemesBotTestToken
        channel_id = ext.MemesChannelTestId
        database_filename = ext.DatabaseTestFilename

    setup_app(database_filename, argv[1:])

    # tools.print_delays()

    if test_mode:
        ext.logger.info('test mode')

    bot = CMemesBot(ext.IdVkGera, bot_token, channel_id)
    bot.start_bot()

    try:
        sys.exit(ext.App.exec_())
    except Exception as e:
        ext.logger.error('main: exception while execution: {}'.format(e))


if __name__ == '__main__':
    main(sys.argv[1:])
