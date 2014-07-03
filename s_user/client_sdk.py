import os
import requests


class ClientSDK(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_forwarded_resource(self, name):
        url = self._client_url('forwarded-resource', name)
        response = requests.get(url)

        print response
        print response.headers
        print response.text

        if response.status_code == 401:
            second_response = requests.post(response.headers['Location'],
                    headers={'Authorization': 'API Key ' + self.api_key})

            if second_response.status_code == 200:
                return second_response.json()

    def _client_url(self, *path):
        return os.path.join(os.environ['CLIENT_URL'], *path)
