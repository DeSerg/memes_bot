import logging
import sqlite3

import extern as ext

import tools.tools as tools

ColumnNameId = 'id'
ColumnNameUserId = 'user_id'
ColumnNameAlbumId = 'album_id'
ColumnNamePhotoId = 'photo_id'
ColumnNamePhotoMd5 = 'photo_md5'

TableNamePhotoQueue = 'photo_queue'
TableNamePhotosUsed = 'photos_used'
TableNameAlbumIds = 'album_ids'

class CDatabaseManager:

    class __CDatabaseManager:

        def __init__(self):
            self.__connection = sqlite3.connect(ext.DatabaseFilename)

        def __is_photo_in_queue(self, photo_id):
            cursor = self.__connection.cursor()
            cursor.execute("SELECT * FROM {} WHERE {} = '{}';".format(
                TableNamePhotoQueue,
                ColumnNameId,
                photo_id
            ))
            record = cursor.fetchone()
            result = record is not None
            return result

        def __add_photo_to_queue(self, photo, photo_id):
            cursor = self.__connection.cursor()
            cursor.execute("INSERT INTO {} VALUES ('{}', {}, {}, {});".format(
                TableNamePhotoQueue,
                photo_id,
                photo.owner_id,
                photo.album_id,
                photo.id
            ))
            self.__connection.commit()

        def __remove_photo_from_queue(self, photo_id):
            cursor = self.__connection.cursor()
            cursor.execute("DELETE FROM {} WHERE {} = {};".format(
                TableNamePhotoQueue,
                ColumnNameId,
                photo_id,
            ))
            self.__connection.commit()

        def __is_photo_used(self, photo_md5):
            cursor = self.__connection.cursor()
            cursor.execute("SELECT * FROM {} WHERE {} = '{}';".format(
                TableNamePhotosUsed,
                ColumnNamePhotoMd5,
                photo_md5
            ))
            record = cursor.fetchone()
            result = record is not None
            return result

        def __set_photo_used(self, photo, photo_md5):
            cursor = self.__connection.cursor()
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
            self.__connection.commit()

        def load_album_ids(self):
            cursor = self.__connection.cursor()
            cursor.execute("SELECT * FROM {};".format(TableNameAlbumIds))
            records = cursor.fetchall()
            album_ids = list(map(lambda rec: rec[0], records))
            return album_ids

        def add_album_id(self, album_id):
            cursor = self.__connection.cursor()
            cursor.execute("INSERT INTO {} VALUES ('{}');".format(
                TableNameAlbumIds,
                album_id
            ))
            self.__connection.commit()

        def verify_photos(self, photos):

            for photo in photos:
                photo_id = tools.generate_photo_id(photo)
                if not self.__is_photo_in_queue(photo_id):
                    self.__add_photo_to_queue(photo, photo_id)

        def photo_used(self, photo_md5):
            return self.__is_photo_used(photo_md5)

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
