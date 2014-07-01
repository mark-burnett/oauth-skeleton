import logging
import os
from s_client.views import app
from urlparse import urlparse


def port():
    url = urlparse(os.environ['CLIENT_URL'])
    return url.port


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=port(), host='0.0.0.0')
