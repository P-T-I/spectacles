"""
app_logger.py
=============
"""
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler

from spectacles.helpers.logger_class import HelperLogger, HostnameFilter


class AppLogger(HelperLogger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s"
        )

        crf = RotatingFileHandler(
            filename=self.config.LOG_FILE_PATH, maxBytes=100000000, backupCount=5
        )
        crf.setLevel(logging.DEBUG)
        crf.setFormatter(formatter)
        self.addHandler(crf)

        formatter = logging.Formatter(
            "%(asctime)s [%(hostname)s] - %(name)-8s - %(levelname)-8s - %(message)s"
        )

        if self.config.SYSLOG_ENABLE:
            syslog = SysLogHandler(
                address=(self.config.SYSLOG_SERVER, int(self.config.SYSLOG_PORT)),
                facility=SysLogHandler.LOG_LOCAL0,
            )

            syslog.setLevel(logging.DEBUG)
            syslog.addFilter(HostnameFilter())
            syslog.setFormatter(formatter)
            self.addHandler(syslog)
