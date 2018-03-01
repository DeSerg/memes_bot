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
DatabaseFilename = 'memes_bot_databes.sqlite3'


# telegram
MemesBotToken = '521889438:AAHCG8IV1MEMCEEN7MAqbA9Bz2nKNru5afE'
MemesChannelId = '@best_of_memes'


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

