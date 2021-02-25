import logging

from flask import request, abort, jsonify

from spectacles.helpers.app_logger import AppLogger
from . import token_auth
from ..app.models import users
from ..auth.views import verify_password
from ..helpers.objects.token_class import Token

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


@token_auth.route("/token_auth", methods=["GET", "POST"])
def index():

    r = request

    if r.method == "GET":
        get_data = dict(request.args)

        logger.info(get_data)

        if hasattr(r, "authorization") and r.authorization is not None:
            authentication = r.authorization

            if authenticate(authentication):
                the_token = Token(**get_data)
                return jsonify(the_token.build_token())
            else:
                return abort(401, "invalid credentials provided...")
        else:
            return abort(401, "missing credentials in request...")
    elif r.method == "POST":
        # fetch form data
        post_data = dict(request.json)

        logger.info(post_data)


def authenticate(auth_dict):

    # do something cunning with database...
    if "username" in auth_dict.keys() and "password" in auth_dict.keys():

        check_user = users.query.filter(users.username == auth_dict["username"]).first()

        if check_user and verify_password(auth_dict["password"], check_user.password):
            return True

    return False
