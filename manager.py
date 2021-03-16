# this module primary focus is for use inside the docker container of spectacles.
from pathlib import Path

from gevent import monkey

monkey.patch_all()

import logging
import os
import time
from subprocess import run, PIPE, STDOUT

from flask_script import Manager
from gevent.pywsgi import WSGIServer

from set_version import VERSION
from spectacles.helpers.app_logger import AppLogger
from spectacles.helpers.background_class import BackgroundTasks
from spectacles.webapp.run import create_app

__version__ = VERSION

app = create_app(version=__version__)

manager = Manager(app)

logging.setLoggerClass(AppLogger)

logger = logging.getLogger("spectacles")

current_dir = os.path.dirname(os.path.realpath(__file__))


@manager.command
def runserver():

    # Check if this is a first run of the container
    if not os.path.exists("/app/data/db/INIT_COMPLETED"):
        init_database = "python db_migrate.py -i -m -u"

        run(
            init_database,  # nosec
            stdout=PIPE,
            stderr=STDOUT,
            universal_newlines=True,
            shell=True,
            cwd=current_dir,
        )

        Path("/app/data/db/INIT_COMPLETED").touch()

    if os.path.exists(app.config["SPECTACLES_WEB_TLS_CERT_PATH"]) and os.path.exists(
        app.config["SPECTACLES_WEB_TLS_KEY_PATH"]
    ):

        http_server = WSGIServer(
            ("", 5050),
            app,
            certfile=app.config["SPECTACLES_WEB_TLS_CERT_PATH"],
            keyfile=app.config["SPECTACLES_WEB_TLS_KEY_PATH"],
            log=logger,
        )
    else:
        http_server = WSGIServer(("", 5050), app, log=logger,)

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
