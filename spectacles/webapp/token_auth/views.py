import json
import logging

import requests
from flask import request, abort, jsonify

from spectacles.helpers.app_logger import AppLogger
from . import token_auth
from ..app.models import users
from ..config import Config
from ..helpers.objects.token_class import Token

# fix for background process which cannot access this runtime variable
try:
    from ..run import oidc
except ImportError:
    pass

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

        auth_result, auth_data = authenticate(authentication, get_data)

        if auth_result:
            the_token = Token(**auth_data)
            return jsonify(the_token.build_token())
        else:
            return abort(401, "invalid credentials provided...")
    else:
        return abort(401, "missing credentials in request...")


def authenticate(auth_dict, get_data):

    if "username" in auth_dict.keys() and "password" in auth_dict.keys():

        if config.OPENID_LOGIN:
            logger.info("Authenticating against OIDC provider...")

            logger.info(f"Issuer: {oidc.client_secrets.get('issuer')}")
            # Check credentials against OIDC provider
            with requests.session() as session:
                headers = {"Content-Type": "application/x-www-form-urlencoded"}

                data = {
                    "username": auth_dict["username"],
                    "password": auth_dict["password"],
                    "client_id": f"{oidc.client_secrets.get('client_id')}",
                    "client_secret": f"{oidc.client_secrets.get('client_secret')}",
                    "grant_type": "password",
                }

                result = session.post(
                    url=f"{oidc.client_secrets.get('issuer')}/protocol/openid-connect/token",
                    data=data,
                    headers=headers,
                    verify=False,
                )

                if result.status_code == 200:
                    data = json.loads(result.content.decode("utf-8"))

                    if "access_token" in data:
                        logger.info("Authentication success!")

                        logger.info("Fetching userinfo....")
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Authorization": f"Bearer {data['access_token']}",
                        }

                        userinfo = session.get(
                            url=f"{oidc.client_secrets.get('issuer')}/protocol/openid-connect/userinfo",
                            headers=headers,
                            verify=False,
                        )

                        userinfo = json.loads(userinfo.content.decode("utf-8"))

                        get_data["account"] = userinfo["trigram"].lower()

                        logger.info("Done fetching userinfo!")

                        return True, get_data
                elif str(result.status_code).startswith("5"):
                    logger.error(f"{result} --> {result.content.decode('utf-8')}")
                    raise ConnectionError
                elif str(result.status_code).startswith("4"):
                    logger.error(f"{result} --> {result.content.decode('utf-8')}")
                    raise ConnectionRefusedError

        else:
            logger.info("Authenticating against local database...")
            # Check credentials against local database
            check_user = users.query.filter(
                users.username == auth_dict["username"]
            ).first()

            if check_user and check_user.verify_password(auth_dict["password"]):
                logger.info("Authentication success!")
                return True, get_data

    return False, 0
