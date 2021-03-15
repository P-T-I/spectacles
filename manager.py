from gevent import monkey

monkey.patch_all()

import logging
from spectacles.helpers.app_logger import AppLogger


import time

from flask_script import Manager

from set_version import VERSION
from spectacles.helpers.background_class import BackgroundTasks
from spectacles.webapp.run import create_app
from gevent.pywsgi import WSGIServer

__version__ = VERSION

app = create_app(version=__version__)

manager = Manager(app)

logging.setLoggerClass(AppLogger)

logger = logging.getLogger("spectacles")


@manager.command
def runserver():
    http_server = WSGIServer(
        ("", 5050),
        app,
        certfile=app.config["SPECTACLES_WEB_TLS_CERT_PATH"],
        keyfile=app.config["SPECTACLES_WEB_TLS_KEY_PATH"],
        log=logger,
    )
    http_server.serve_forever()


@manager.command
def runbackground():
    starttime = time.time()

    bg = BackgroundTasks(app=app)

    while True:
        bg.run()
        time.sleep(
            float(app.config["SPECTACLES_BACKGROUND_UPDATE"])
            - (
                (time.time() - starttime)
                % float(app.config["SPECTACLES_BACKGROUND_UPDATE"])
            )
        )


if __name__ == "__main__":
    manager.run()
