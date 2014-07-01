import logging
import os
from s_resource.views import app
from urlparse import urlparse


def port():
    url = urlparse(os.environ['RESOURCE_URL'])
    return url.port


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=port(), host='0.0.0.0')
