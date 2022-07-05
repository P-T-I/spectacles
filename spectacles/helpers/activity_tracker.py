import logging
import time

from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import activity
from spectacles.webapp.helpers.constants.common import activity_level
from spectacles.webapp.run import db

logging.setLoggerClass(AppLogger)


class ActivityTracker(object):
    def __init__(self, action_type):
        self.action_type = action_type
        self.logger = logging.getLogger(__name__)

    def info(self, msg):
        self.__insert(level=activity_level.INFO, msg=msg)

    def success(self, msg):
        self.__insert(level=activity_level.SUCCESS, msg=msg)

    def warning(self, msg):
        self.__insert(level=activity_level.WARNING, msg=msg)

    def danger(self, msg):
        self.__insert(level=activity_level.DANGER, msg=msg)

    def __insert(self, level, msg):
        try:
            db.session.add(
                activity(
                    level=level,
                    action=self.action_type,
                    msg=msg,
                    log_time=int(time.time()),
                )
            )
            db.session.commit()
            return True
        except Exception as err:
            self.logger.error(f"Error saving activity to database: {err}")
