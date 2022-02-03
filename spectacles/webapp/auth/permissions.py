import logging
from functools import wraps

from flask import abort
from flask_login import current_user

from spectacles.helpers.app_logger import AppLogger

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


def user_required(fn):
    """
    Decorator (@user_required) that enforces that users with the READ_ONLY role are not allowed on a specific endpoint.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if current_user.role.lower() != "user":
            return fn(*args, **kwargs)
        else:
            logger.warning(
                "User {} tried to perform illegal action to "
                "user protected endpoints!!".format(current_user.username)
            )
            abort(403)

    return wrapper


def admin_required(fn):
    """
    Decorator (@admin_required) that enforces that only users with the ADMIN role are allowed on a specific endpoint.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if current_user.role.lower() != "admin":
            logger.warning(
                "User {} tried to perform illegal action to "
                "admin protected endpoints!!".format(current_user.username)
            )
            abort(403)
        else:
            return fn(*args, **kwargs)

    return wrapper
