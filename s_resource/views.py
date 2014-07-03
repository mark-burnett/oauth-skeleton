from . import backend
from . import models
from flask import jsonify, request
from flask.views import MethodView
from s_common.validate import validate_request_roles
import flask


class ResourceView(MethodView):
    # NOTE This is vulnerable to multiple timing attacks.
    def get(self, name=None):
        if not request_is_authenticated():
            return '', 401

        s = backend.Session()

        resource = s.query(models.Resource).get(name)
        if resource and validate_request_roles(scopes='resource',
                allowed_roles=resource.allowed_roles):
            return jsonify(resource.as_dict), 200

        else:
            return '', 403


def request_is_authenticated():
    return 'Authorization' in request.headers


app = flask.Flask('Resource')
app.add_url_rule('/resource/<string:name>',
        view_func=ResourceView.as_view('resource'))
