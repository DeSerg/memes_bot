import extern as ext

from tools import vk_tools

from modules.db import CDatabaseManager


class CMemesBot:

    def __init__(self, user_id):

        self.db_manager = CDatabaseManager.instance()

        self.user_id = user_id
        self.album_ids = self.db_manager.load_album_ids()
        self.albums = [vk_tools.CAlbum(self.user_id, album_id) for album_id in ext.AlbumIds]

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