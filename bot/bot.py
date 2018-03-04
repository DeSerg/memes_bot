from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from random import randint
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import extern as ext

import tools.tools as tools
import tools.telegram_tools as t_tools
import tools.vk_tools as vk_tools
import tools.network as ntools

from modules.db import CDatabaseManager


CommandStart = 'start'
CommandHelp = 'help'
CommandUpdatePhotos = 'update'
CommandAddAlbum = 'add_album'
CommandRemoveAlbum = 'remove_album'
CommandPostNext = 'post_next'


LIST_OF_ADMINS = [ext.IdTelegramPopelmopel, ext.IdTelegramGera]


def check_allowed(update):
    user_id = update.message.from_user.id
    if user_id in LIST_OF_ADMINS:
        return True

    ext.logger.warning("bot.py: restricted: unauthorized access denied for {}.".format(user_id))
    update.message.reply_text('Извините, эта команда недоступна')
    return False


class CMemesBot(QObject):

    def __init__(self,
                 vk_user_id,
                 telegram_bot_token,
                 telegram_channel_id,
                 post_interval_min=ext.PostDelayMin,
                 post_interval_max=ext.PostDelayMax,
                 update_interval=ext.UpdateDelay,
                 best_minute=ext.MinuteBest):

        super().__init__()

        self.user_id = vk_user_id

        self.telegram_bot_token = telegram_bot_token
        self.telegram_channel_id = telegram_channel_id

        self.post_interval_min = post_interval_min
        self.post_interval_max = post_interval_max

        self.update_interval = update_interval

        self.best_minute = best_minute

        self.post_timer = QTimer()
        self.post_timer.timeout.connect(self.on_post_timer)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.on_update_timer)

        self.db_manager = CDatabaseManager.instance()

        self.album_ids = self.db_manager.load_album_ids()
        self.albums = [vk_tools.CAlbum(self.user_id, album_id) for album_id in self.album_ids]

        # self.bot = telegram.Bot(token=ext.MemesBotToken)

        self.updater = Updater(self.telegram_bot_token)

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

        dp.add_handler(CallbackQueryHandler(self.handle_callback))

        # log all errors
        dp.add_error_handler(self.error)

    def start_bot(self):
        delay = tools.current_delay(self.post_interval_min, self.post_interval_max, self.best_minute)
        self.post_timer.singleShot(delay * ext.TimerSecondsMultiplier, self.on_post_timer)
        self.update_timer.start(self.update_interval * ext.TimerSecondsMultiplier)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()

    def __send_picture(self, picture_filepath, show_buttons=False, caption=''):
        try:

            with open(picture_filepath, 'rb') as f:
                if show_buttons:
                    self.updater.bot.sendPhoto(self.telegram_channel_id, photo=f, caption=caption,
                                               reply_markup=t_tools.build_reply_markup())
                else:
                    self.updater.bot.sendPhoto(self.telegram_channel_id, photo=f, caption=caption)

            return True
        except Exception as e:
            ext.logger.error('CMemesBot: __send_picture: failed to send photo: exception: {}'.format(e))
            return False

    def handle_callback(self, bot, update):
        ext.logger.info('CMemesBot: handle_callback')
        callback_query = update.callback_query
        ext.logger.info('CMemesBot: handle_callback: callback_query inited')

        message = callback_query.message
        ext.logger.info('CMemesBot: handle_callback: message inited')
        message_id = message.message_id
        ext.logger.info('CMemesBot: handle_callback: message id inited')

        user = callback_query.from_user
        ext.logger.info('CMemesBot: handle_callback: user inited')
        user_id = callback_query.from_user.id
        ext.logger.info('CMemesBot: handle_callback: user id inited')

        voice = callback_query.data

        callback_info = 'user: {} {}, message_id: {}, voice: {}'.format(
            user.first_name,
            user.last_name,
            message_id,
            voice
        )

        ext.logger.info('CMemesBot: handle_callback: {}: obtaining started'.format(callback_info))

        success, message = self.db_manager.change_feedback(voice, message_id, user_id)
        if not success:
            ext.logger.error('CMemesBot: handle_callback: {}: failed to change feedback'.format(callback_info))
            return

        likes, neutrals, dislikes = self.db_manager.count_feedback(message_id)

        if likes is None:
            ext.logger.info('CMemesBot: handle_callback: {}: failed to count likes...'.format(callback_info))
            return

        if neutrals is None:
            ext.logger.info('CMemesBot: handle_callback: {}: failed to count neutrals...'.format(callback_info))
            return

        if dislikes is None:
            ext.logger.info('CMemesBot: handle_callback: {}: failed to count dislikes...'.format(callback_info))
            return

        bot.editMessageReplyMarkup(
            chat_id=self.telegram_channel_id,
            message_id=message_id,
            reply_markup=t_tools.build_reply_markup(likes, neutrals, dislikes))

        bot.answerCallbackQuery(callback_query.id, message)

        ext.logger.info('CMemesBot: handle_callback: {}: success'.format(callback_info))

    def error(self, bot, update, error):
        ext.logger.warning('Update "{}" caused error "{}"'.format(update, error))

    def command_start(self, bot, update):
        update.message.reply_text('Hi!')

    def command_help(self, bot, update):

        message = update.message
        ext.logger.info(dir(message))
        user = message.from_user
        user_id = user.id
        if user_id not in LIST_OF_ADMINS:
            ext.logger.warning("bot.py: restricted: unauthorized access denied for {}.".format(user_id))
            return

        command_list = self.command_map.keys()
        command_list = list(map(lambda command: '/' + command, command_list))
        update.message.reply_text('Commands:\n' + '\n'.join(command_list))

    def update_photos(self):
        statistics = []
        for album_id in self.album_ids:
            ext.logger.info('\nCMemesBot: update_photos: at album: {}'.format(album_id))
            album_info = ['Альбом: {}'.format(album_id)]

            # photos_ = vk_tools.photo_list(self.user_id, album_id)

            photos = vk_tools.load_photos_for_album(self.user_id, album_id)
            if photos is None:
                album_info.append('Не удалось загрузить фото...')
                continue

            ext.logger.info('CMemesBot: update_photos: photos total: {}'.format(len(photos)))
            album_info.append('Фотографий всего: {}'.format(len(photos)))

            photos_added = self.db_manager.verify_photos(photos)
            ext.logger.info('CMemesBot: update_photos: photos added: {}'.format(photos_added))
            album_info.append('Фотографий добавлено в очередь: {}'.format(photos_added))
            statistics.append('\n'.join(album_info))

        return '\n\n'.join(statistics)

    def command_update_photos(self, bot, update):
        ext.logger.info('CMemesBot: command_update_photos')

        if not check_allowed(update):
            return

        try:
            result = self.update_photos()
        except Exception as e:
            ext.logger.error('bot.py: command_update_photos: exception: {}'.format(e))
            result = 'Неудача...'

        update.message.reply_text(result)

    def command_add_album(self, bot, update):
        if not check_allowed(update):
            return
        # TODO get album id
        album_id = 0
        if album_id not in self.album_ids:
            # TODO: verify if album exists
            self.db_manager.add_album_id(album_id)
            self.album_ids.append(album_id)

        update.message.reply_text('Успех!')

    def command_remove_album(self, bot, update):
        if not check_allowed(update):
            return

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

        if not self.__send_picture(ext.FilenameTemp, show_buttons=True):
            return 'Не удалось отправить изображение в канал...'

        return 'Успех!'

    def command_post_next(self, bot, update):
        ext.logger.info('CMemesBot: command_post_next')
        if not check_allowed(update):
            return

        try:
            result = self.post_next()
        except Exception as e:
            ext.logger.error('bot.py: command_post_next: exception: {}'.format(e))
            result = 'Неудача...'

        ext.logger.info('CMemesBot: command_post_next: {}'.format(result))
        update.message.reply_text(result)

    @pyqtSlot(name='on_post_timer')
    def on_post_timer(self):
        ext.logger.info('CMemesBot: on_post_timer')

        try:
            self.post_next()
        except Exception as e:
            ext.logger.error('CMemesBot: on_post_timer: failed to post next: exception: {}'.format(e))

        delay = tools.current_delay(self.post_interval_min, self.post_interval_max, self.best_minute)
        ext.logger.info('CMemesBot: on_post_timer: post successful, next in {} minutes'.format(delay / 60))
        self.post_timer.singleShot(delay * ext.TimerSecondsMultiplier, self.on_post_timer)

    @pyqtSlot(name='on_update_timer')
    def on_update_timer(self):
        ext.logger.info('CMemesBot: on_update_timer')
        self.update_photos()
