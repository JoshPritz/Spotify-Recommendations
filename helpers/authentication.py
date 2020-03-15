import json
import urllib.error
import urllib.request

from helpers import utilities

API_TUTOR_TOKEN = 'API.fda8c628-f8f0-448d-aad8-42c2fcd067ec'


def get_token(url):

    try:
        response = urllib.request.urlopen(url + '?auth_manager_token=' + API_TUTOR_TOKEN)
        data = response.read()
        results = data.decode('utf-8', 'ignore')
        return json.loads(results)['token']

    except urllib.error.HTTPError as e:
        # give a good error message:
        error = utilities.get_error_message(e, url)

    raise Exception(error)
