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
ColumnNameMessageId = 'message_id'
ColumnNameTelegramUserId = 'telegram_user_id'

TableNamePhotoQueue = 'photo_queue'
TableNamePhotosUsed = 'photos_used'
TableNameAlbumIds = 'album_ids'

TableNameLikes = 'likes'
TableNameNeutrals = 'neutrals'
TableNameDislikes = 'dislikes'

TableNamesFeedback = [TableNameLikes, TableNameNeutrals, TableNameDislikes]


AddVoiceMessage = 'Ваш голос был учтен'
# RemoveVoiceMessage = 'Ваш голос был удален'
RemoveVoiceMessage = 'Ты охуел голос убирать!'


class CDatabaseManager:

    class __CDatabaseManager:

        def __init__(self, database_filename=ext.DatabaseFilename):
            self.database_filename = database_filename

        def create_connection(self):
            return sqlite3.connect(self.database_filename)

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

                photo_urls = list(filter(lambda url: url is not None, [photo.get(key_url) for key_url in vk_tools.KeysPhotoUrl]))
                if not photo_urls:
                    ext.logger.warning('__CDatabaseManager: __add_photo_to_queue: photo has no url')
                    return

                photo_url = photo_urls[-1]

                cursor.execute("INSERT INTO {} VALUES ('{}', {}, '{}', {}, '{}');".format(
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

        def __get_next_photo_from_queue(self, random):
            fail_value = None, None
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                random_cmd = ''
                if random:
                    random_cmd = 'ORDER BY RANDOM()'
                cursor.execute("SELECT {}, {} FROM {} {} LIMIT 1;".format(
                    ColumnNameId,
                    ColumnNamePhotoUrl,
                    TableNamePhotoQueue,
                    random_cmd
                ))
                record = cursor.fetchone()
                return record[0], record[1]
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __get_next_photo_from_queue: exception: {}'.format(e))
                return fail_value

        # photos used
        def __is_photo_used(self, photo_id_text):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM {} WHERE {} = '{}';".format(
                    TableNamePhotosUsed,
                    ColumnNameId,
                    photo_id_text
                ))
                record = cursor.fetchone()
                result = record is not None
                return result
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __is_photo_used: exception: {}'.format(e))

        def __set_photo_used(self, photo_id_text):
            try:

                owner_id, album_id, photo_id = photo_id_text.split('_')

                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO {} ({}, {}, {}, {}) VALUES ('{}', {}, '{}', {});".format(
                    TableNamePhotosUsed,
                    ColumnNameId,
                    ColumnNameUserId,
                    ColumnNameAlbumId,
                    ColumnNamePhotoId,
                    photo_id_text,
                    owner_id,
                    album_id,
                    photo_id
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
        def get_next_photo_url_from_queue(self, random=False):
            photo_id_text, photo_url = self.__get_next_photo_from_queue(random)
            if photo_id_text is not None and photo_url is not None:
                self.__remove_photo_from_queue(photo_id_text)
                self.__set_photo_used(photo_id_text)
            return photo_url

        # likes
        def __add_feedback(self, table_name, message_id, telegram_user_id):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("INSERT INTO {} VALUES ({}, {})".format(
                    table_name,
                    message_id,
                    telegram_user_id
                ))
                connection.commit()
                return True
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __add_feedback: exception: {}'.format(e))
                return False

        def __remove_feedback(self, table_name, message_id, telegram_user_id):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM {} WHERE {} = {} and {} = {};".format(
                    table_name,
                    ColumnNameMessageId,
                    message_id,
                    ColumnNameTelegramUserId,
                    telegram_user_id
                ))

                connection.commit()
                return True
            except Exception as e:
                ext.logger.error('__CDatabaseManager: __remove_feedback: exception: {}'.format(e))
                return False

        def change_feedback(self, table_name, message_id, telegram_user_id):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM {} WHERE {} = {} AND {} = {};".format(
                    table_name,
                    ColumnNameMessageId,
                    message_id,
                    ColumnNameTelegramUserId,
                    telegram_user_id
                ))
                record = cursor.fetchone()
                feedback_added = record is not None

                if feedback_added:
                    return self.__remove_feedback(table_name, message_id, telegram_user_id), RemoveVoiceMessage
                else:
                    success = True
                    for tn in TableNamesFeedback:
                        if tn == table_name:
                            continue
                        if not self.__remove_feedback(tn, message_id, telegram_user_id):
                            success = False
                    if not self.__add_feedback(table_name, message_id, telegram_user_id):
                        success = False
                    return success, AddVoiceMessage

            except Exception as e:
                ext.logger.error('__CDatabaseManager: __change_feedback: exception: {}'.format(e))
                return False, None

        def __count_feedback(self, table_name, message_id):
            try:
                connection = self.create_connection()
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM {} WHERE {} = {};".format(
                    table_name,
                    ColumnNameMessageId,
                    message_id
                ))
                record = cursor.fetchone()
                return record[0]

            except Exception as e:
                ext.logger.error('__CDatabaseManager: __count_feedback: exception: {}'.format(e))
                return None

        def count_feedback(self, message_id):
            likes = self.__count_feedback(TableNameLikes, message_id)
            neutrals = self.__count_feedback(TableNameNeutrals, message_id)
            dislikes = self.__count_feedback(TableNameDislikes, message_id)
            return likes, neutrals, dislikes


        # other
        def verify_photos(self, photos):

            photos_added = 0

            for photo in photos:
                photo_id_text = tools.get_photo_id_from_photo(photo)

                if photo_id_text is None:
                    continue

                if self.__is_photo_used(photo_id_text):
                    continue

                photo_in_queue = self.__is_photo_in_queue(photo_id_text)
                if photo_in_queue is None:
                    ext.logger.warning('__CDatabaseManager: verify_photos: failed to check if photo is in queue')
                    continue

                if not photo_in_queue:
                    self.__add_photo_to_queue(photo, photo_id_text)
                    photos_added += 1

            return photos_added

    __instance = None

    @staticmethod
    def instance():
        if not CDatabaseManager.__instance:
            CDatabaseManager.__instance = CDatabaseManager.__CDatabaseManager()
        return CDatabaseManager.__instance

    def __init__(self, database_filename):
        if not CDatabaseManager.__instance:
            CDatabaseManager.__instance = CDatabaseManager.__CDatabaseManager(database_filename)
        else:
            logging.warning('CDatabaseManager: CDatabaseManager: singleton has already been initialized')
