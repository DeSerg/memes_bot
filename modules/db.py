import logging
import sqlite3

import extern as ext


class CDatabaseManager:

    class __CDatabaseManager:

        def __init__(self):
            self.connection = sqlite3.connect(ext.DatabaseFilename)


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
