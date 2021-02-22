from flask import Blueprint

home = Blueprint("home", __name__)

from . import views  # noqa: F401
from . import users  # noqa: F401
