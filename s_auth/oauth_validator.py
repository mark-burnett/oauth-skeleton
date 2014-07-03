from . import models
from oauthlib.oauth2 import RequestValidator


class OAuthRequestValidator(RequestValidator):
    def __init__(self, session):
        self.session = session

    def _get_client(self, client_id):
        return self.session.query(models.Client
                ).filter_by(client_id=client_id).first()

    def validate_client_id(self, client_id, request):
        return self._get_client(client_id) is not None

    def validate_redirect_uri(self, client_id, redirect_uri, request):
        # XXX Needed
        # Is the client allowed to use the supplied redirect_uri? i.e. has
        # the client previously registered this EXACT redirect uri.
        return True

    def validate_scopes(self, client_id, scopes, client, request):
        c = self._get_client(client_id)

        if scopes:
            requested_scopes = set(scopes)
        else:
            requested_scopes = set()
        allowed_scopes = set(c.scopes)

        result = requested_scopes.issubset(allowed_scopes)

        return result

    def get_default_scopes(self, client_id, request):
        return self._get_client(client_id).scopes

    def validate_response_type(self, client_id, response_type, client, request):
        return response_type == 'code'

    def save_authorization_code(self, client_id, code, request):
        key = self.session.query(models.Key
                ).filter_by(key=request.headers['Authorization'][8:]).one()

        ac = models.AuthorizationCode(code=code['code'],
                api_key=key, client=self._get_client(client_id))
        ac.scope = request.scopes
        self.session.add(ac)
        self.session.commit()

    def client_authentication_required(self, request):
        return True

    # XXX DO STUFF
    def authenticate_client(self, request):
        c = self._get_client(request.client_id)
        if request.client_secret == c.client_secret:
            request.client = c
            return True

        else:
            return False

    def validate_grant_type(self, client_id, grant_type, client, request):
        return grant_type == 'authorization_code'

    def validate_code(self, client_id, code, client, request):
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client):
        return True

    def save_bearer_token(self, token, request):
        code = self.session.query(models.AuthorizationCode
                ).filter_by(code=request.code).one()

        r = models.RefreshToken(token=token['refresh_token'],
                authorization_code=code)
        a = models.AccessToken(token=token['access_token'], refresh_token=r)
        self.session.add(r)
        self.session.add(a)
        self.session.commit()

    def invalidate_authorization_code(self, client_id, code, request):
        # XXX Should flag the code as inactive/invalid
        pass
