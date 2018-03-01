from PyQt5.QtCore import QCoreApplication

import sys

from modules.db import CDatabaseManager

from bot.bot import CMemesBot

import extern as ext
import tools.tools as tools


def setup_app(argv):

    ext.App = QCoreApplication(argv)

    tools.prepare_log(ext.LogFilepath)

    CDatabaseManager()

    ext.logger.info('Started')


def main(argv):

    setup_app(argv)

    bot = CMemesBot(ext.IdVkGera, 60 * 30, 60 * 120)
    bot.start_bot()

    try:
        sys.exit(ext.App.exec_())
    except Exception as e:
        ext.logger.error('main: exception while execution: {}'.format(e))


if __name__ == '__main__':
    main(sys.argv[1:])