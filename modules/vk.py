import logging

from modules.vk import VkAPIError


VkAccessToken = 'a29a964a53a1b6329d0011a089ab0a496b6ef4886b1585261ad6d4f2bd817b8910e894aa3e89602fd2565'

VkSession = vk.AuthSession(access_token=VkAccessToken)
VkApi = vk.API(VkSession)


class CAlbum:

    def __init__(self, user_id, album_id):
        self.user_id = user_id
        self.album_id = album_id

        self.photos = None

    def load_photos(self):
        try:
            self.photos = VkApi.photos.get(owner_id=self.user_id, album_id=self.album_id)
        except VkAPIError as e:
            self.photos = None
            logging.error('CAlbum: load_photos: exception: {}'.format(e))
