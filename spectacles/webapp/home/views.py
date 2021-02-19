import logging

from flask import render_template, send_from_directory, current_app
from flask_login import login_required

from spectacles.helpers.app_logger import AppLogger
from . import home

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


@home.route("/")
@login_required
def index():

    return render_template("pages/home.html", header="Dashboard",)


@home.route("/avatars/<path:filename>")
@login_required
def get_avatar(filename):
    return send_from_directory(current_app.config["AVATARS_SAVE_PATH"], filename)
