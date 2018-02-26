import logging

import vk
from vk.exceptions import VkAPIError

import tools.network as ntools


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


def load_photos_for_album(user_id, album_id):
    try:
        photos = VkApi.photos.get(owner_id=user_id, album_id=album_id)
        return photos
    except VkAPIError as e:
        logging.error('CAlbum: load_photos: exception: {}'.format(e))
        return None


def load_photo(photo, filepath):
    return ntools.get_file(filepath, photo.photo_1280)
