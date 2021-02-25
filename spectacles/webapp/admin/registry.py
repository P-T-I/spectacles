import logging

from flask import render_template, request, abort
from flask_login import login_required

from spectacles.webapp.app.models import registry
from . import admin
from .forms import RegistryForm
from ..auth.permissions import admin_required
from ...helpers.app_logger import AppLogger

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


@admin.route("/registries")
@login_required
@admin_required
def get_registries():

    form = RegistryForm()

    total_registry = registry.query.filter().all()

    return render_template("pages/registry.html", header="Registries", registry=total_registry, form=form)


@admin.route("/registries/test_connection", methods=["POST"])
@login_required
@admin_required
def test_connection_registries():
    post_data = dict(request.json)

    return abort(503, "CONNECTION REFUSED")
