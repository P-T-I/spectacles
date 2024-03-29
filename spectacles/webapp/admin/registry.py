import logging
import time
from collections import defaultdict

from flask import render_template, request, abort, jsonify
from flask_login import login_required, current_user

from spectacles.webapp.app.models import registry, namespaces, repository
from . import admin
from .forms import RegistryForm
from ..auth.permissions import admin_required
from ..helpers.constants.common import msg_status, action_types
from ..run import db
from ...docker_reg_api.Docker_reg_api import DockerRegistryApi
from ...helpers.activity_tracker import ActivityTracker
from ...helpers.app_logger import AppLogger

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)

activity_track = ActivityTracker(action_type=action_types.USER)


@admin.route("/registries")
@login_required
@admin_required
def get_registries():

    form = RegistryForm()

    total_registry, count_dict = get_count_dict()

    return render_template(
        "pages/registry.html",
        header="Registries",
        registry=total_registry,
        count_dict=count_dict,
        form=form,
    )


def get_count_dict():

    total_registry = registry.query.filter().all()

    count_dict = defaultdict(str)

    for each in total_registry:
        repo_count = repository.query.filter(
            repository.namespacesid.in_(
                db.session.query(namespaces.id)
                .filter(namespaces.registryid == each.id)
                .all()
            )
        ).count()

        ns_count = namespaces.query.filter(namespaces.registryid == each.id).count()

        count_dict[
            each.uri
        ] = f"{ns_count} namespaces containing {repo_count} repositories"

    return total_registry, count_dict


@admin.route("/registries/test_connection", methods=["POST"])
@login_required
@admin_required
def test_connection_registries():
    post_data = dict(request.json)

    address = (post_data["uri"].split(":")[0], post_data["uri"].split(":")[1])

    if "ssl" in post_data:
        dr = DockerRegistryApi(address=address)
    else:
        dr = DockerRegistryApi(address=address, protocol="http")

    pong = dr.ping()

    if pong:
        if isinstance(pong, dict):
            return jsonify(pong)
        else:
            return abort(503)
    else:
        return abort(503)


@admin.route("/registries/add", methods=["POST"])
@login_required
@admin_required
def add_registries():
    post_data = dict(request.json)

    try:
        reg = registry()

        reg.uri = post_data["uri"]
        if post_data["ssl"] == "y":
            reg.protocol = "https"
        else:
            reg.protocol = "http"
        reg.service_name = post_data["service_name"]
        reg.created = int(time.time())

        db.session.add(reg)
        db.session.commit()
        activity_track.success(
            f"User {current_user.username} added registry on uri: {post_data['uri']}"
        )

        total_registry, count_dict = get_count_dict()

        return {
            "registry_data": render_template(
                "partials/registry_list.html",
                registry=total_registry,
                count_dict=count_dict,
            ),
            "status": msg_status.OK,
            "msg": "Registry added!",
        }
    except Exception as err:
        return jsonify({"status": msg_status.NOK, "msg": f"Error encountered: {err}"})


@admin.route("/registries/delete", methods=["POST"])
@login_required
@admin_required
def del_registries():
    post_data = dict(request.json)

    try:
        registry.query.filter(registry.id == post_data["id"]).delete()
        db.session.commit()
        activity_track.danger(
            f"User {current_user.username} deleted registry with ID: {post_data['id']}"
        )

        total_registry = registry.query.filter().all()

        return {
            "registry_data": render_template(
                "partials/registry_list.html", registry=total_registry
            ),
            "status": msg_status.OK,
            "msg": "Registry deleted!",
        }
    except Exception as err:
        return jsonify({"status": msg_status.NOK, "msg": f"Error encountered: {err}"})
