import logging

from flask import request, abort, jsonify

from spectacles.helpers.app_logger import AppLogger
from . import token_auth
from ..app.models import users
from ..config import Config
from ..helpers.objects.token_class import Token

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)

config = Config()


@token_auth.route("/token_auth")
def index():

    r = request

    get_data = dict(request.args)

    logger.info(f"Requested resource: {get_data}")

    if hasattr(r, "authorization") and r.authorization is not None:
        authentication = r.authorization

        if authenticate(authentication):
            the_token = Token(**get_data)
            return jsonify(the_token.build_token())
        else:
            return abort(401, "invalid credentials provided...")
    else:
        return abort(401, "missing credentials in request...")


def authenticate(auth_dict):

    if "username" in auth_dict.keys() and "password" in auth_dict.keys():

        if config.OPENID_LOGIN:
            # Check credentials against OIDC provider
            pass
        else:
            # Check credentials against local database
            check_user = users.query.filter(
                users.username == auth_dict["username"]
            ).first()

            if check_user and check_user.verify_password(auth_dict["password"]):
                return True

    return False
