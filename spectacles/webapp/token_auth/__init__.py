from flask import Blueprint

token_auth = Blueprint("token_auth", __name__)

from . import views  # noqa: F401
