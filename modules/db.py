import logging
import sqlite3

import extern as ext

import tools.tools as tools
import tools.vk_tools as vk_tools

ColumnNameId = 'id'
ColumnNameUserId = 'user_id'
ColumnNameAlbumId = 'album_id'
ColumnNamePhotoId = 'photo_id'
ColumnNamePhotoMd5 = 'photo_md5'
ColumnNamePhotoUrl = 'photo_url'

TableNamePhotoQueue = 'photo_queue'
TableNamePhotosUsed = 'photos_used'
TableNameAlbumIds = 'album_ids'

class CDatabaseManager:

    class __CDatabaseManager:

        def __init__(self):
            pass

        def create_connection(self):
            return sqlite3.connect(ext.DatabaseFilename)

        # private
        # photo queue
        def __is_photo_in_queue(self, photo_id):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM {} WHERE {} = '{}';".format(
                    TableNamePhotoQueue,
                    ColumnNameId,
                    photo_id
                ))
                record = cursor.fetchone()
                result = record is not None
                return result
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __is_photo_in_queue: exception: {}'.format(e))
                return None

        def __add_photo_to_queue(self, photo, photo_id_str):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()

                owner_id = photo.get(vk_tools.KeyPhotoOwnerId)
                album_id = photo.get(vk_tools.KeyPhotoAlbumId)
                photo_id = photo.get(vk_tools.KeyPhotoId)
                photo_url = photo.get(vk_tools.KeyPhotoUrl)

                cursor.execute("INSERT INTO {} VALUES ('{}', {}, {}, {}, '{}');".format(
                    TableNamePhotoQueue,
                    photo_id_str,
                    owner_id,
                    album_id,
                    photo_id,
                    photo_url
                ))
                connection.commit()
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __add_photo_to_queue: exception: {}'.format(e))

        def __remove_photo_from_queue(self, photo_id):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM {} WHERE {} = '{}';".format(
                    TableNamePhotoQueue,
                    ColumnNameId,
                    photo_id,
                ))
                connection.commit()
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __remove_photo_from_queue: exception: {}'.format(e))

        def __get_next_photo_from_queue(self):
            fail_value = None, None
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT {}, {} FROM {};".format(
                    ColumnNameId,
                    ColumnNamePhotoUrl,
                    TableNamePhotoQueue
                ))
                record = cursor.fetchone()
                return record[0], record[1]
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __get_next_photo_from_queue: exception: {}'.format(e))
                return fail_value

        # photos used
        def __is_photo_used(self, photo_md5):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM {} WHERE {} = '{}';".format(
                    TableNamePhotosUsed,
                    ColumnNamePhotoMd5,
                    photo_md5
                ))
                record = cursor.fetchone()
                result = record is not None
                return result
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __is_photo_used: exception: {}'.format(e))

        def __set_photo_used(self, photo, photo_md5):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO {} ({}, {}, {}, {}) VALUES ('{}', {}, {}, {}});".format(
                    TableNamePhotosUsed,
                    ColumnNamePhotoMd5,
                    ColumnNameUserId,
                    ColumnNameAlbumId,
                    ColumnNamePhotoId,
                    photo_md5,
                    photo.owner_id,
                    photo.album_id,
                    photo.id
                ))
                connection.commit()
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __set_photo_used: exception: {}'.format(e))

        # public
        # album ids
        def load_album_ids(self):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM {};".format(TableNameAlbumIds))
                records = cursor.fetchall()
                album_ids = list(map(lambda rec: rec[0], records))
                return album_ids
            except Exception as e:
                ext.logger.error('__CDatabaseManager: load_album_ids: exception: {}'.format(e))
                return []

        def add_album_id(self, album_id):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO {} VALUES ('{}');".format(
                    TableNameAlbumIds,
                    album_id
                ))
                connection.commit()
            except Exception as e:
                ext.logger.error('__CDatabaseManager: add_album_id: exception: {}'.format(e))

        def remove_album_id(self, album_id):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM {} WHERE {} = '{}';".format(
                    TableNameAlbumIds,
                    ColumnNameAlbumId,
                    album_id,
                ))
                connection.commit()
            except Exception as e:
                ext.logger.error('__CDatabaseManager: remove_album_id: exception: {}'.format(e))

        # photo queue
        def get_next_photo_url_from_queue(self):
            photo_id, photo_url = self.__get_next_photo_from_queue()
            if photo_id is not None and photo_url is not None:
                self.__remove_photo_from_queue(photo_id)
            return photo_url

        # photos used
        def photo_used(self, photo_md5):
            return self.__is_photo_used(photo_md5)

        # other
        def verify_photos(self, photos):

            for photo in photos:
                photo_id = tools.get_photo_id_from_photo(photo)

                if photo_id is None:
                    continue

                photo_in_queue = self.__is_photo_in_queue(photo_id)
                if photo_in_queue is None:
                    continue

                if not photo_in_queue:
                    self.__add_photo_to_queue(photo, photo_id)

    __instance = None

    @staticmethod
    def instance():
        if not CDatabaseManager.__instance:
            CDatabaseManager.__instance = CDatabaseManager.__CDatabaseManager()
        return CDatabaseManager.__instance

    def __init__(self):
        if not CDatabaseManager.__instance:
            CDatabaseManager.__instance = CDatabaseManager.__CDatabaseManager()
        else:
            logging.warning('CDatabaseManager: CDatabaseManager: singleton has already been initialized')
