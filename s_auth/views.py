from . import backend
from . import models
from .oauth_validator import OAuthRequestValidator
from flask import jsonify, request
from flask.views import MethodView
from oauthlib.oauth2 import MobileApplicationServer, WebApplicationServer
import flask
import logging
import urllib


LOG = logging.getLogger(__file__)


# -- OAuth setup
session = backend.Session()
oauth_validator = OAuthRequestValidator(session)
oauth_implicit = MobileApplicationServer(oauth_validator)
oauth_web = WebApplicationServer(oauth_validator)


# -- Views
class WebAuthorizeView(MethodView):
    def get(self):
        return '', 401, {'Location': request.url}

    def post(self):
        # XXX Need a better way to extract data (why doesn't c_a_r do this?)
        scopes, request_data = oauth_web.validate_authorization_request(
                uri=request.url, body=request.data, headers=request.headers)

        api_key = request.headers['Authorization'][8:]
        LOG.debug('API key: (%s)', api_key)

        headers, body, status_code = oauth_web.create_authorization_response(
                uri=request.url, headers=request.headers, scopes=scopes,
                credentials={'api_key': api_key})

        LOG.info('authorize c_a_r: (%s, %s, %s)', headers, body,
            status_code)

        return '', status_code, headers


class ImplicitAuthorizeView(MethodView):
    def get(self):
        return '', 401, {'Location': request.url}

    def post(self):
        # XXX Need a better way to extract data (why doesn't c_a_r do this?)
        scopes, request_data = oauth_implicit.validate_authorization_request(
                uri=request.url, body=request.data, headers=request.headers)

        api_key = request.headers['Authorization'][8:]
        LOG.debug('API key: (%s)', api_key)

        headers, body, status_code = oauth_implicit.create_authorization_response(
                uri=request.url, headers=request.headers, scopes=scopes,
                credentials={'api_key': api_key})

        LOG.info('authorize c_a_r: (%s, %s, %s)', headers, body,
            status_code)

        return '', status_code, headers


class TokenView(MethodView):
    def post(self):
        regenerated_body = urllib.urlencode(request.form)

        headers, body, status_code = oauth_web.create_token_response(
                uri=request.url, headers=request.headers, body=regenerated_body)

        return body, status_code, headers


class RequestTuple(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client = None


class ValidateView(MethodView):
    def post(self):
        data = request.get_json()

        if self.validate_client(data) and self.validate_token(data):
            return '', 200

        return '', 403


    def validate_client(self, data):
        r = RequestTuple(client_id=data['client_id'],
                client_secret=data.get('client_secret'))

        if oauth_validator.client_authentication_required(r):
            return oauth_validator.authenticate_client(r)

        else:
            return True

    def validate_token(self, data):
        bearer_token = request.headers.get('Authorization', '')[7:]
        access_token = session.query(models.AccessToken).filter_by(
                token=bearer_token).first()

        if not access_token:
            return False

        allowed_scopes = set(access_token.scopes)
        requested_scopes = set(data['scopes'].split(' '))
        if not requested_scopes.issubset(allowed_scopes):
            return False

        user = access_token.user
        allowed_roles = set(data.get('allowed_roles', []))
        user_roles = set([r.name for r in user.roles])

        if not allowed_roles.intersection(user_roles):
            LOG.debug('role mismatch.  allowed = %s  user = %s',
                    allowed_roles, user_roles)
            return False

        return True


# -- Flask app
app = flask.Flask('Auth')
app.add_url_rule('/web-authorize',
        view_func=WebAuthorizeView.as_view('web-authorize'))
app.add_url_rule('/implicit-authorize',
        view_func=ImplicitAuthorizeView.as_view('implicit-authorize'))
app.add_url_rule('/token', view_func=TokenView.as_view('token'))
app.add_url_rule('/validate', view_func=ValidateView.as_view('validate'))
