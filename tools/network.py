import requests

import extern as ext

import tools.files as files


LoadSuccess = 0
LoadErrorNetwork = 1
LoadError = 2


def get_file(filepath, url):

    try:

        if not files.create_dir_for_filepath(filepath):
            ext.logger.error('network.py: get_file: directory for file {} was not created...'.format(filepath))
            return False

        response = requests.get(url, stream=True)

        if response.status_code != requests.codes.ok:
            if response.status_code >= 500:
                ext.logger.error('network.py: get_file: bad response: status code: %d' % response.status_code)
            return False

        with open(filepath, 'wb') as out_file:
            for chunk in response:
                out_file.write(chunk)

    except requests.RequestException as e:
        ext.logger.error('network.py: get_file: requests exception: ' + str(e))
        return False

    except Exception as e:
        ext.logger.error('network.py: get_file: exception: ' + str(e))
        return False

    return True

