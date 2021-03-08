import logging

from flask import render_template, send_from_directory, current_app
from flask_login import login_required

from spectacles.helpers.app_logger import AppLogger
from . import home
from .namespaces import get_total_namespaces
from .repositories import fetch_repos
from ..app.models import users, groups, registry

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


@home.route("/")
@login_required
def index():

    ns_count = len(get_total_namespaces())

    all_repos = fetch_repos()

    repo_count = 0

    for each in all_repos:
        repo_count += len(all_repos[each])

    user_count = users.query.count()
    group_count = groups.query.count()

    reg_count = registry.query.count()

    return render_template("pages/home.html", header="Dashboard", **locals())


@home.route("/avatars/<path:filename>")
@login_required
def get_avatar(filename):
    return send_from_directory(current_app.config["AVATARS_SAVE_PATH"], filename)
