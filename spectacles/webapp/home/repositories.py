from collections import defaultdict

from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from . import home
from .namespaces import get_total_namespaces
from ..app.models import registry, repository, namespaces, tags
from ..helpers.constants.common import msg_status, action_types
from ..run import db
from ...docker_reg_api.Docker_reg_api import DockerRegistryApi
from ...helpers.activity_tracker import ActivityTracker

activity_track = ActivityTracker(action_type=action_types.USER)


@home.route("/repositories")
@login_required
def get_repositories():

    ret_dict = fetch_repos()

    return render_template(
        "pages/repositories.html", header="Repositories", ret_dict=ret_dict
    )


def fetch_repos():
    ret_dict = defaultdict(lambda: defaultdict(list))

    all_registries = db.session.query(registry.uri, registry.id).all()

    for register in all_registries:

        filter_in = (
            db.session.query(namespaces.id)
            .filter(namespaces.registryid == register.id)
            .all()
        )

        if current_user.role == "admin":
            ret_dict[register.uri] = (
                repository.query.filter(
                    repository.namespacesid.in_([x.id for x in filter_in])
                )
                .order_by(repository.path)
                .all()
            )
        else:
            ret_dict[register.uri] = (
                repository.query.filter(
                    repository.namespacesid.in_([x.id for x in filter_in])
                )
                .filter(
                    repository.namespacesid.in_([x.id for x in get_total_namespaces()])
                )
                .order_by(repository.path)
                .all()
            )

    return ret_dict


@home.route("/repositories/get_repodetails", methods=["POST"])
@login_required
def get_repodetails():
    post_data = dict(request.json)

    all_tags = (
        tags.query.filter(tags.repositoryid == post_data["id"])
        .order_by(tags.version.desc())
        .all()
    )

    return render_template("partials/repo_details.html", repo_det=all_tags)


@home.route("/repositories/del_repo", methods=["POST"])
@login_required
def del_repo():
    post_data = dict(request.json)

    try:
        my_tag = tags.query.filter(tags.id == post_data["id"]).first()

        selected_tag = my_tag.version

        dr = DockerRegistryApi(
            (
                my_tag.repository.namespace.registry.uri.split(":")[0],
                my_tag.repository.namespace.registry.uri.split(":")[1],
            ),
            protocol=my_tag.repository.namespace.registry.protocol,
            docker_service_name=my_tag.repository.namespace.registry.service_name,
        )

        dr.delete_repository(name=post_data["name"], digest=post_data["digest"])

        tags.query.filter(tags.id == post_data["id"]).delete()

        db.session.commit()
        activity_track.danger(
            "User {} deleted repo: {}".format(current_user.username, post_data["name"])
        )

        all_tags = (
            tags.query.filter(tags.repositoryid == post_data["id"])
            .order_by(tags.version.desc())
            .all()
        )

        return {
            "repo_details": render_template(
                "partials/repo_details.html", repo_det=all_tags
            ),
            "status": msg_status.OK,
            "msg": "Repository {}:{} deleted!".format(post_data["name"], selected_tag),
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )
