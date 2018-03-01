from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from random import randint
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import extern as ext

from tools import vk_tools
import tools.network as ntools

from modules.db import CDatabaseManager


CommandStart = 'command_start'
CommandHelp = 'command_help'
CommandUpdatePhotos = 'update'
CommandAddAlbum = 'command_add_album'
CommandRemoveAlbum = 'command_remove_album'
CommandPostNext = 'post_next'


class CMemesBot(QObject):

    def __init__(self, user_id, post_interval, update_interval):

        super().__init__()

        self.user_id = user_id
        self.post_interval = post_interval / 2
        self.post_interval_min_addition = 0
        self.post_interval_max_addition = post_interval

        self.update_interval = update_interval

        self.post_timer = QTimer()
        self.post_timer.timeout.connect(self.on_post_timer)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.on_update_timer)

        self.db_manager = CDatabaseManager.instance()

        self.album_ids = self.db_manager.load_album_ids()
        self.albums = [vk_tools.CAlbum(self.user_id, album_id) for album_id in self.album_ids]

        # self.bot = telegram.Bot(token=ext.MemesBotToken)

        self.updater = Updater(ext.MemesBotToken)

        # Get the dispatcher to register handlers
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        self.command_map = {
            CommandStart: self.command_start,
            CommandHelp: self.command_help,
            CommandUpdatePhotos: self.command_update_photos,
            CommandAddAlbum: self.command_add_album,
            CommandRemoveAlbum: self.command_remove_album,
            CommandPostNext: self.command_post_next
        }

        for command, method in self.command_map.items():
            dp.add_handler(CommandHandler(command, method))

        # log all errors
        dp.add_error_handler(self.error)

    def start_bot(self):
        self.post_timer.singleShot(self.post_interval * ext.TimerSecondsMultiplier, self.on_post_timer)
        self.update_timer.start(self.update_interval * ext.TimerSecondsMultiplier)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()

    def __send_picture(self, picture_filepath, caption=''):
        try:
            with open(picture_filepath, 'rb') as f:
                self.updater.bot.sendPhoto(ext.MemesChannelId, photo=f, caption=caption)

            return True
        except Exception as e:
            ext.logger.error('CMemesBot: __send_picture: failed to send photo: exception: {}'.format(e))
            return False

    def error(self, bot, update, error):
        ext.logger.warning('Update "{}" caused error "{}"'.format(update, error))

    def command_start(self, bot, update):
        update.message.reply_text('Hi!')

    def command_help(self, bot, update):
        command_list = self.command_map.keys()
        command_list = list(map(lambda command: '/' + command, command_list))
        update.message.reply_text('Commands:\n' + '\n'.join(command_list))

    def update_photos(self):
        statistics = []
        for album_id in self.album_ids:
            album_info = ['Альбом: {}'.format(album_id)]

            # photos_ = vk_tools.photo_list(self.user_id, album_id)

            photos = vk_tools.load_photos_for_album(self.user_id, album_id)
            if photos is None:
                album_info.append('Не удалось загрузить фото...')
                continue

            album_info.append('Фотографий всего: {}'.format(len(photos)))

            photos_added = self.db_manager.verify_photos(photos)
            album_info.append('Фотографий добавлено в очередь: {}'.format(photos_added))
            statistics.append('\n'.join(album_info))

        return '\n\n'.join(statistics)

    def command_update_photos(self, bot, update):
        result = self.update_photos()
        update.message.reply_text(result)

    def command_add_album(self, bot, update):
        # TODO get album id
        album_id = 0
        if album_id not in self.album_ids:
            # TODO: verify if album exists
            self.db_manager.add_album_id(album_id)
            self.album_ids.append(album_id)

        update.message.reply_text('Успех!')

    def command_remove_album(self, bot, update):
        # TODO get album id
        album_id = 0
        if album_id in self.album_ids:
            self.album_ids.remove(album_id)
            self.db_manager.remove_album_id(album_id)

        update.message.reply_text('Успех!')

    def post_next(self):

        photo_url = self.db_manager.get_next_photo_url_from_queue(True)

        if not ntools.get_file(ext.FilenameTemp, photo_url):
            ext.logger.error('CMemesBot: post_next: failed to load photo for url {}'.format(photo_url))
            return 'Не удалось загрузить фото...'

        if not self.__send_picture(ext.FilenameTemp):
            return 'Не удалось отправить изображение в канал...'

        return 'Успех!'

    def command_post_next(self, bot, update):
        result = self.post_next()
        update.message.reply_text(result)

    @pyqtSlot(name='on_post_timer')
    def on_post_timer(self):
        ext.logger.info('CMemesBot: on_post_timer')

        try:
            self.post_next()
        except Exception as e:
            ext.logger.error('CMemesBot: on_post_timer: failed to post next: exception: {}'.format(e))

        interval_addition = randint(self.post_interval_min_addition, self.post_interval_max_addition)
        interval = (self.post_interval + interval_addition) * ext.TimerSecondsMultiplier
        self.post_timer.singleShot(interval, self.on_post_timer)

    @pyqtSlot(name='on_update_timer')
    def on_update_timer(self):
        ext.logger.info('CMemesBot: on_update_timer')
        self.update_photos()
