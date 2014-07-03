from flask import redirect, request
from flask.views import MethodView
from requests_oauthlib import OAuth2Session
from s_common.auth import auth_url
import flask
import os
import requests


class ForwardedResourceView(MethodView):
    def get(self, name):
        if 'state' in request.args:
            oauth_session = OAuth2Session(os.environ['CLIENT_CLIENT_ID'],
                    state=request.args['state'])
            token = oauth_session.fetch_token(auth_url('token'),
                    client_secret=os.environ['CLIENT_CLIENT_SECRET'],
                    authorization_response=request.url)

            response = requests.get(self.forward_url(name), headers={
                    'Authorization': 'Bearer %s' % token['access_token'],
                })
            return response.text, response.status_code

        else:
            oauth_session = OAuth2Session(os.environ['CLIENT_CLIENT_ID'],
                    redirect_uri=request.url)
            authorization_url, state = oauth_session.authorization_url(
                    auth_url('authorize'))

            return redirect(authorization_url)

    def forward_url(self, name):
        return '%s/resource/%s' % (os.environ['RESOURCE_URL'], name)


app = flask.Flask('Client')
app.add_url_rule('/forwarded-resource/<string:name>',
        view_func=ForwardedResourceView.as_view('forwarded-resource'))
