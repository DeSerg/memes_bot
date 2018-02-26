import logging
import json

KeyAscTime = 'asctime'
KeyClientPcMac = 'client_pc_mac'
KeyClientPcIp = 'client_pc_ip'
KeyUserId = 'user_id'
KeyLevelName = 'levelname'
KeyMessage = 'message'

LogFormat = '%(asctime)-25s %(name)-15s %(levelname)-8s %(message)s'
LogFormatNetwork = '%({})s - %({})s - %({})s - %({})s - %({})s - %({})s'.format(KeyAscTime, KeyClientPcMac, KeyClientPcIp, KeyUserId, KeyLevelName, KeyMessage)


class LogstashFormatter(logging.Formatter):
    def __init__(self):
        super(LogstashFormatter, self).__init__()

    def format(self, record):
        data = {
            KeyAscTime: record.asctime,
            KeyClientPcMac: record.client_pc_mac,
            KeyClientPcIp: record.client_pc_ip,
            KeyUserId: record.user_id,
            KeyLevelName: record.levelname,
            KeyMessage: record.message
        }

        return json.dumps(data)