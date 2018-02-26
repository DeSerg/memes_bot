import extern as ext
from modules import vk


class CMemesBot:

    def __init__(self):

        self.user_id = ext.UserId
        self.albums = [vk.CAlbum(self.user_id, album_id) for album_id in ext.AlbumIds]

    def update_photos(self):

        for album in self.albums:
            pass



