import logging

# general
App = None

# log
LogPath = 'log/'
LogFilename = 'memes_bot.log'
LogFilepath = LogPath + LogFilename

LoggerNameMemesBot = 'logger_name_memes_bot'

logger = logging.getLogger(LoggerNameMemesBot)

# database
DatabaseFilename = 'memes_bot_database.sqlite3'
DatabaseTestFilename = 'memes_bot_test_database.sqlite3'


# telegram
IdTelegramPopelmopel = 112946213
IdTelegramGera = 121593595

MemesChannelId = '@old_memes'
MemesChannelTestId = '@best_of_memes_test'


# other
FilenameTemp = 'temp'

TimerSecondsMultiplier = 1000

IdVkSerg = '35280311'
IdVkGera = '249354007'

IdVkMemesAlbum = '000'
IdVkRunCityAlbum = '214728539'
IdVkDotAlbum = '210810034'

UserId = IdVkSerg
AlbumIds = [IdVkRunCityAlbum, IdVkDotAlbum]

