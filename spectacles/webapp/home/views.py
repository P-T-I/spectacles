import logging

from flask import render_template

from spectacles.helpers.app_logger import AppLogger
from . import home

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


@home.route("/")
def index():

    return render_template("pages/home.html", header="Dashboard",)
