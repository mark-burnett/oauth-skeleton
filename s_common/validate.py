from flask import request
from .auth import auth_url
import requests
import simplejson


def validate_request_roles(scopes, allowed_roles, client_id,
        client_secret=None):
    request_data = {
        'allowed_roles': allowed_roles,
        'scopes': scopes,
        'client_id': client_id,
    }
    if client_secret:
        request_data['client_secret'] = client_secret

    request_headers = {
        'Authorization': request.headers['Authorization'],
        'Content-Type': 'application/json',
    }

    response = requests.post(auth_url('validate'),
            headers=request_headers, data=simplejson.dumps(request_data))

    return response.status_code == 200
