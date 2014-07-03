import os
import urllib


def auth_url(path, **query_args):
    base_url = os.path.join(os.environ['AUTH_URL'], path)

    if query_args:
        query_string = urllib.urlencode(query_args)
        return '%s?%s' % (base_url, query_string)

    else:
        return base_url
