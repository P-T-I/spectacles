from flask import Blueprint

home = Blueprint("home", __name__)

from . import views  # noqa: F401
from . import cps  # noqa: F401
from . import namespaces  # noqa: F401
from . import repositories  # noqa: F401
