import logging

from flask import request, abort, jsonify

from spectacles.helpers.app_logger import AppLogger
from . import token_auth
from ..helpers.objects.token_class import Token

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


@token_auth.route("/token_auth", methods=["GET", "POST"])
def index():

    r = request

    post_data = dict(request.args)

    logger.info(post_data)

    the_token = Token()

    if hasattr(r, "authorization") and r.authorization is not None:
        authentication = r.authorization

        if authorize(authentication):
            return jsonify(the_token.build_token())
        else:
            return abort(401, "invalid credentials provided...")
    else:
        return abort(401, "missing credentials in request...")

    # abort(401, "invalid or missing auth credentials...")


def authorize(auth_dict):

    # do something cunning with database...

    if auth_dict["username"] == "foo" and auth_dict["password"] == "bar":
        return True

    return False


def get_header():

    # with open()

    header = {
        "typ": "JWT",
        "alg": "ES256",
        "kid": "PYYO:TEWU:V7JH:26JV:AQTZ:LJC3:SXVJ:XGHA:34F2:2LAQ:ZRMK:Z7Q6",
    }

    return header
