import logging
import json
import requests

import vk_api
import vk
from vk.exceptions import VkAPIError

import extern as ext

import tools.network as ntools
import tools.credentials as credentials

login, password = credentials.login, credentials.password
vk_session = vk_api.VkApi(login, password)

try:
    vk_session.auth()
except vk_api.AuthError as error_msg:
    ext.logger.error('vk auth error: {}'.format(error_msg))

VkApi = vk_session.get_api()

# app_id = 6386515

VkAccessToken = '68283ff955f9650ad70177aaa2d112d8d616b939c034518af4b561f2ac615df3f34387be459cc5975207d'
# VkAccessToken = '3d0818b4b520a549fa178d21f735605870e8a2b6efdb0ff7362cf1de6c5e9b0f3c97d8114921d14509e35'
# VkAccessToken = 'c536193edd0e5586b9eec26b0d29ef3dcedb5e27e8a4aac22fcc05dabb7227922b8b93074d8683a06b0a9'

# VkSession = vk.AuthSession(app_id=app_id, user_login=login, user_password=password)
# VkApi = vk.API(VkSession)

KeyPhotosCount = 'count'
KeyPhotosItems = 'items'

KeyPhotoOwnerId = 'owner_id'
KeyPhotoAlbumId = 'album_id'
KeyPhotoId = 'id'
KeyPhotoUrl = 'photo_807'

KeysPhotoUrl = [
    'photo_75',
    'photo_130',
    'photo_604',
    'photo_807',
    'photo_1280',
    'photo_2560'
]


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

        photos_count = photos.get(KeyPhotosCount)
        photos_items = photos.get(KeyPhotosItems)

        if photos_count > len(photos_items):
            current_count = len(photos_items)
            while current_count < photos_count:
                photos = VkApi.photos.get(owner_id=user_id, album_id=album_id, offset=current_count)

                current_items = photos.get(KeyPhotosItems)
                current_count += len(current_items)

                photos_items += current_items

        return photos_items

    except VkAPIError as e:
        logging.error('CAlbum: load_photos: exception: {}'.format(e))
        return None


def vkMethod(method, d={}):
    print("Запрос к API")
    url = 'https://api.vk.com/method/%s' % (method)
    d.update({'access_token': '160568916b3a8ea63849882edfa2a56f43d564eb77c30b9e0059d4735a8ed1d33786f8f9013390fdfbcaf'})

    response = json.loads(requests.post(url, d).content)

    if 'error' in response:
        print('VK API error: %s' % (response['error']['error_msg']))
    else:
        print("Ответ получен")

    return response


def photo_list(user_id, album_id):
    d = {"aid": album_id}
    try:
        response = VkApi.method("photos.get", d)
    except Exception as e:
        ext.logger.error('vk_tools: photo_list: exception: {}'.format(e))
    ids = []
    for photo in response["response"]:
        if photo.has_key("src_xxxbig"):
            url = photo["src_xxxbig"]
        elif photo.has_key("src_xxbig"):
            url = photo["src_xxbig"]
        elif photo.has_key("src_xbig"):
            url = photo["src_xbig"]
        elif photo.has_key("src_big"):
            url = photo["src_big"]
        else:
            url = photo["src"]

        photo_id = photo["pid"]
        ids.append(photo_id)

    return ids


def load_photo(photo, filepath):
    return ntools.get_file(filepath, photo.photo_1280)


