from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from random import randint
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

import extern as ext

import tools.tools as tools
import tools.telegram_tools as t_tools
import tools.vk_tools as vk_tools
import tools.network as ntools

import modules.db as db
from modules.db import CDatabaseManager


CommandStart = 'start'
CommandHelp = 'help'
CommandUpdatePhotos = 'update'
CommandAddAlbum = 'add_album'
CommandRemoveAlbum = 'remove_album'
CommandPostNext = 'post_next'
CommandSuggestMem = 'suggest_mem'


AdminsList = [ext.IdTelegramPopelmopel, ext.IdTelegramGera]
AdminsListVerifying = [ext.IdTelegramPopelmopel]


MessageFormatStart = '''Приветик!
Этот бот позволяет предлагать мемы в канал {}.
Чтобы предложить мем, просто отправь его боту!
Если твой мем будет достаточно старым и несмешным, он будет запощен😉🤪
'''

MessageFormatNotifySuggestionReceived = 'Спасибо за мем!😉'
MessageFormatSuggestedByUser = 'Прислал {} через {}'

MessageFormatSuggestedByUserAdmin = 'By @{}'
MessageSuggestedUsernameStart = 4

MessageMemAccepted = 'Мем успешно запощен!'
MessageMemRejected = 'Мем отвергнут...'


def is_user_admin(update):
    user_id = update.message.from_user.id
    if user_id in AdminsList:
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
                 best_minute=ext.MinuteBest,
                 show_buttons=False):

        super().__init__()

        self.user_id = vk_user_id

        self.telegram_bot_token = telegram_bot_token
        self.telegram_channel_id = telegram_channel_id

        self.post_interval_min = post_interval_min
        self.post_interval_max = post_interval_max

        self.update_interval = update_interval

        self.best_minute = best_minute

        self.show_buttons = show_buttons

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
        dp.add_handler(MessageHandler(Filters.photo, self.handle_mem_suggestion))

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

    def __post_mem_from_file(self, picture_filepath, caption=''):
        try:
            with open(picture_filepath, 'rb') as f:
                reply_markup = None
                if self.show_buttons:
                    reply_markup = t_tools.build_reply_markup()

                self.updater.bot.sendPhoto(self.telegram_channel_id,
                                           photo=f,
                                           caption=caption,
                                           reply_markup=reply_markup)

            return True
        except Exception as e:
            ext.logger.error('CMemesBot: __post_mem_from_file: failed to send photo: exception: {}'.format(e))
            return False

    def __post_mem_from_message(self, message, caption=''):
        try:
            photos = message.photo
            if not photos:
                ext.logger.warning('CMemesBot: __post_mem_from_message: no photo in message {}'.format(message.message_id))
                return False

            photo = t_tools.choose_photo_max_size(photos)
            reply_markup = None
            if self.show_buttons:
                reply_markup = t_tools.build_reply_markup()

            self.updater.bot.sendPhoto(self.telegram_channel_id,
                                       photo=photo.file_id,
                                       caption=caption,
                                       reply_markup=reply_markup)
            return True
        except Exception as e:
            ext.logger.error('CMemesBot: __post_mem_from_message: failed to send photo: exception: {}'.format(e))
            return False

    def handle_callback_accept_mem(self, bot, update):
        ext.logger.info('CMemesBot: handle_callback_accept_mem')
        try:
            message = update.callback_query.message

            username = message.caption[MessageSuggestedUsernameStart:]
            message_caption = MessageFormatSuggestedByUser.format(username, ext.MemesChannelId)

            self.__post_mem_from_message(message, caption=message_caption)

            message_id = message.message_id
            chat_id = message.chat_id

            bot.editMessageReplyMarkup(chat_id=chat_id, message_id=message_id)
            bot.sendMessage(chat_id=chat_id, text=MessageMemAccepted)

        except Exception as e:
            ext.logger.error('CMemesBot: handle_callback_accept_mem: exception: {}'.format(e))

    def handle_callback_reject_mem(self, bot, update):
        ext.logger.info('CMemesBot: handle_callback_reject_mem')

        try:
            message = update.callback_query.message
            message_id = message.message_id
            chat_id = message.chat_id

            bot.editMessageReplyMarkup(chat_id=chat_id, message_id=message_id)
            bot.sendMessage(chat_id=chat_id, text=MessageMemRejected)

        except Exception as e:
            ext.logger.error('CMemesBot: handle_callback_accept_mem: exception: {}'.format(e))
            try:
                update.message.reply_text('Все очень плохо...')
            except:
                ext.logger.error('CMemesBot: handle_callback_accept_mem: failed to tell about exception...')

    def handle_callback_voice(self, bot, update):
        ext.logger.info('CMemesBot: handle_callback_voice')
        callback_query = update.callback_query

        message = callback_query.message
        message_id = message.message_id

        user = callback_query.from_user
        user_id = user.id

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

    def handle_callback(self, bot, update):
        ext.logger.info('CMemesBot: handle_callback')

        try:
            callback_query = update.callback_query
            callback_data = callback_query.data

            if callback_data == t_tools.CallbackPostSuggestionAccept:
                self.handle_callback_accept_mem(bot, update)
            elif callback_data == t_tools.CallbackPostSuggestionReject:
                self.handle_callback_reject_mem(bot, update)
            elif callback_data in db.TableNamesFeedback:
                self.handle_callback_voice(bot, update)
        except Exception as e:
            ext.logger.error('CMemesBot: handle_callback: exception: {}'.format(e))

    def error(self, bot, update, error):
        ext.logger.warning('Update "{}" caused error "{}"'.format(update, error))

    def command_start(self, bot, update):
        update.message.reply_text(MessageFormatStart.format(ext.MemesChannelId))

    def command_help(self, bot, update):

        message = update.message
        ext.logger.info(dir(message))
        user = message.from_user
        user_id = user.id
        if user_id not in AdminsList:
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

        if not is_user_admin(update):
            return

        try:
            result = self.update_photos()
        except Exception as e:
            ext.logger.error('bot.py: command_update_photos: exception: {}'.format(e))
            result = 'Неудача...'

        update.message.reply_text(result)

    def command_add_album(self, bot, update):
        if not is_user_admin(update):
            return
        # TODO get album id
        album_id = 0
        if album_id not in self.album_ids:
            # TODO: verify if album exists
            self.db_manager.add_album_id(album_id)
            self.album_ids.append(album_id)

        update.message.reply_text('Успех!')

    def command_remove_album(self, bot, update):
        if not is_user_admin(update):
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

        if not self.__post_mem_from_file(ext.FilenameTemp):
            return 'Не удалось отправить изображение в канал...'

        return 'Успех!'

    def command_post_next(self, bot, update):
        ext.logger.info('CMemesBot: command_post_next')
        if not is_user_admin(update):
            return

        try:
            result = self.post_next()
        except Exception as e:
            ext.logger.error('bot.py: command_post_next: exception: {}'.format(e))
            result = 'Неудача...'

        ext.logger.info('CMemesBot: command_post_next: {}'.format(result))
        update.message.reply_text(result)

    def handle_mem_suggestion(self, bot, update):
        try:
            update.message.reply_text(MessageFormatNotifySuggestionReceived)

            if is_user_admin(update):
                self.__post_mem_from_message(update.message)
                return

            t_tools.build_reply_markup_verify_mem()
            message = update.message
            photos = message.photo
            if not photos:
                update.message.reply_text('Ты забыл приложить мем)0')
            photo = t_tools.choose_photo_max_size(photos)

            verify_markup = t_tools.build_reply_markup_verify_mem()

            user_name = message.from_user.username

            for admin_id in AdminsListVerifying:
                self.updater.bot.sendPhoto(
                    admin_id,
                    photo=photo.file_id,
                    caption=MessageFormatSuggestedByUserAdmin.format(user_name),
                    reply_markup=verify_markup)

        except Exception as e:
            ext.logger.error('CMemesBot: handle_mem_suggestion: exception: {}'.format(e))

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
