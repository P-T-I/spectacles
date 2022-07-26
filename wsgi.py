# this module primary focus is for use inside the docker container of spectacles.
from gevent import monkey

monkey.patch_all()

# additional monkey patch for allowing self-signed certificates
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ssl._create_default_https_context = ctx

import click
from flask.cli import with_appcontext
import logging
import os
import time
from subprocess import run, PIPE, STDOUT
from pathlib import Path

from gevent.pywsgi import WSGIServer

from set_version import VERSION
from spectacles.helpers.app_logger import AppLogger
from spectacles.helpers.background_class import BackgroundTasks
from spectacles.webapp.run import create_app

__version__ = VERSION

app = create_app(version=__version__)

logging.setLoggerClass(AppLogger)

logger = logging.getLogger("spectacles")

current_dir = os.path.dirname(os.path.realpath(__file__))


@click.command()
@with_appcontext
def runserver():

    # Check if this is a first run of the container
    if not os.path.exists("/app/data/db/INIT_COMPLETED"):
        init_database = "python3 db_migrate.py -i"
        migrate_database = "python3 db_migrate.py -m"
        update_database = "python3 db_migrate.py -u"

        run(
            init_database,  # nosec
            stdout=PIPE,
            stderr=STDOUT,
            universal_newlines=True,
            shell=True,
            cwd=current_dir,
        )

        run(
            migrate_database,  # nosec
            stdout=PIPE,
            stderr=STDOUT,
            universal_newlines=True,
            shell=True,
            cwd=current_dir,
        )

        run(
            update_database,  # nosec
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
        http_server = WSGIServer(("", 5050), app, log=logger)

    http_server.serve_forever()


@click.command()
@with_appcontext
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


app.cli.add_command(runserver)
app.cli.add_command(runbackground)
