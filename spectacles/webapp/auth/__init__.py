from flask import Blueprint

from ..config import Config

auth = Blueprint("auth", __name__)

from . import views  # noqa: F401

if Config().OPENID_LOGIN:
    from . import openid_login  # noqa: F401

if Config().REGISTER_ENABLED:
    from . import register  # noqa: F401
