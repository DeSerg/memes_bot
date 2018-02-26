import telegram

import extern as ext

from tools import vk_tools
import tools.network as ntools

from modules.db import CDatabaseManager


class CMemesBot:

    def __init__(self, user_id):

        self.user_id = user_id

        self.db_manager = CDatabaseManager.instance()

        self.album_ids = self.db_manager.load_album_ids()
        self.albums = [vk_tools.CAlbum(self.user_id, album_id) for album_id in ext.AlbumIds]

        self.bot = telegram.Bot(token=ext.MemesBotToken)

    def __send_picture(self, picture_filepath, caption=''):
        try:
            with open(picture_filepath, 'rb') as f:
                self.bot.sendPhoto(ext.MemesChannelId, photo=f, caption=caption)
        except Exception as e:
            ext.logger.error('CMemesBot: __send_picture: failed to send photo: exception: {}'.format(e))

    def update_photos(self):

        for album_id in self.album_ids:
            photos = vk_tools.load_photos_for_album(self.user_id, album_id)
            if photos is None:
                continue

            CDatabaseManager.instance().verify_photos(photos)

    def add_album(self, album_id):
        if album_id not in self.album_ids:
            # TODO: verify if album exists
            self.db_manager.add_album_id(album_id)
            self.album_ids.append(album_id)

    def remove_album(self, album_id):
        if album_id in self.album_ids:
            self.album_ids.remove(album_id)
            self.db_manager.remove_album_id(album_id)

    def post_next(self):
        photo_url = self.db_manager.get_next_photo_url_from_queue()

        if not ntools.get_file(ext.FilenameTemp, photo_url):
            ext.logger.error('CMemesBot: post_next: failed to load photo for url {}'.format(photo_url))

        self.__send_picture(ext.FilenameTemp)
