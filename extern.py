import logging

# general
App = None

# log
LogPath = 'log/'
LogFilename = 'memes_bot.log'
LogFilepath = LogPath + LogFilename

KeyAscTime = 'asctime'
KeyClientPcMac = 'client_pc_mac'
KeyClientPcIp = 'client_pc_ip'
KeyUserId = 'user_id'
KeyLevelName = 'levelname'
KeyMessage = 'message'

HttpLogRequestHeaders = {"Content-type": "application/json"}

LogFormat = '%({})s - %({})s - %({})s'.format(KeyAscTime, KeyLevelName, KeyMessage)

LoggerNameMemesBot = 'logger_name_memes_bot'

logger = logging.getLogger(LoggerNameMemesBot)

# database
DatabaseFilename = 'memes_bot_database.sqlite3'
DatabaseTestFilename = 'memes_bot_test_database.sqlite3'


# telegram
IdTelegramPopelmopel = 112946213
IdTelegramGera = 121593595

MemesBotName = '@old_memes_bot'

MemesChannelId = '@old_memes'
MemesChannelTestId = '@best_of_memes_test'


# other
MillisecondsInSecond = 1000
MinutesInHour = 60
HoursInDay = 24
DaysInWeek = 7

FilenameTemp = 'temp'

PostDelayMin = 40 * MinutesInHour
PostDelayMax = 150 * MinutesInHour

UpdateDelay = 120 * MinutesInHour

MinuteBest = 19 * MinutesInHour

PercentCut = 0.1
PercentAdd = 0.2


IdVkSerg = '35280311'
IdVkGera = '249354007'

IdVkMemesAlbum = '000'
IdVkRunCityAlbum = '214728539'
IdVkDotAlbum = '210810034'

UserId = IdVkSerg
AlbumIds = [IdVkRunCityAlbum, IdVkDotAlbum]

