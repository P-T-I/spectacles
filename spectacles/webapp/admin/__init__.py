from flask import Blueprint

admin = Blueprint("admin", __name__)

from . import views  # noqa: F401
from . import users  # noqa: F401
from . import groups  # noqa: F401
from . import registry  # noqa: F401
