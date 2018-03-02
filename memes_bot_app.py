from PyQt5.QtCore import QCoreApplication

import sys

from modules.db import CDatabaseManager

from bot.bot import CMemesBot

import extern as ext
import tools.tools as tools


ArgTest = 'test'


def setup_app(database_filename, argv):

    ext.App = QCoreApplication(argv)

    tools.prepare_log(ext.LogFilepath)

    CDatabaseManager(database_filename)

    ext.logger.info('Started')


def main(argv):

    bot_token = ext.MemesBotToken
    channel_id = ext.MemesChannelId
    database_filename = ext.DatabaseFilename
    test_mode = False

    if len(argv) > 0 and argv[0] == ArgTest:
        test_mode = True
        bot_token = ext.MemesBotTestToken
        channel_id = ext.MemesChannelTestId
        database_filename = ext.DatabaseTestFilename

    setup_app(database_filename, argv[1:])

    if test_mode:
        ext.logger.info('test mode')

    bot = CMemesBot(ext.IdVkGera, bot_token, channel_id, 60 * 30, 60 * 120)
    bot.start_bot()

    try:
        sys.exit(ext.App.exec_())
    except Exception as e:
        ext.logger.error('main: exception while execution: {}'.format(e))


if __name__ == '__main__':
    main(sys.argv[1:])