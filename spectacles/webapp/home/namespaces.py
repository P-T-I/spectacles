import ast
import time

from flask import render_template, request, jsonify
from flask_login import login_required, current_user

from . import home
from .forms import NamespaceForm
from ..app.models import (
    namespaces,
    namespacemembers,
    namespacegroups,
    groupmembers,
    users,
)
from ..helpers.constants.common import msg_status
from ..run import db


@home.route("/namespaces")
@login_required
def get_namespaces():

    form = NamespaceForm()

    total_namespaces = get_total_namespaces()

    return render_template(
        "pages/namespaces.html",
        header="Namespaces",
        namespaces=total_namespaces,
        form=form,
    )


def get_total_namespaces():

    if current_user.role == "admin":
        total_namespaces = namespaces.query.filter().order_by(namespaces.name.asc()).all()
    else:
        total_namespaces_pers = (
            namespaces.query.join(namespacemembers)
            .filter(namespacemembers.userid == current_user.id)
            .filter(namespacemembers.namespaceid == namespaces.id)
            .order_by(namespaces.name.asc())
            .all()
        )

        total_namespaces_group = (
            namespaces.query.join(namespacegroups)
            .filter(
                namespacegroups.groupid.in_(
                    db.session.query(groupmembers.userid)
                    .filter(groupmembers.userid == current_user.id)
                    .all()
                )
            )
            .filter(namespacegroups.namespaceid == namespaces.id)
            .all()
        )

        total_namespaces = total_namespaces_pers + total_namespaces_group

    return total_namespaces


@home.route("/namespaces/add", methods=["POST"])
@login_required
def add_namespaces():
    post_data = dict(request.json)

    try:
        new_ns = namespaces()
        new_ns.name = post_data["name"]
        new_ns.description = post_data["description"]
        new_ns.owner = current_user.id
        new_ns.registryid = int(post_data["registry"])
        new_ns.created = int(time.time())

        db.session.add(new_ns)
        db.session.commit()

        new_ns_member = namespacemembers()
        new_ns_member.userid = current_user.id
        new_ns_member.namespaceid = new_ns.id

        db.session.add(new_ns_member)
        db.session.commit()

        total_namespaces = get_total_namespaces()

        return {
            "namespace_data": render_template(
                "partials/namespace_list.html",
                header="Namespaces",
                namespaces=total_namespaces,
            ),
            "status": msg_status.OK,
            "msg": "Namespace {} created!".format(post_data["name"]),
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@home.route("/namespaces/delete", methods=["POST"])
@login_required
def del_group():
    post_data = dict(request.json)

    try:
        namespaces.query.filter(namespaces.id == post_data["id"]).filter(
            namespaces.owner == current_user.id
        ).delete()
        db.session.commit()

        total_namespaces = get_total_namespaces()

        return {
            "namespace_data": render_template(
                "partials/namespace_list.html",
                header="Namespace",
                namespaces=total_namespaces,
            ),
            "status": msg_status.OK,
            "msg": "Namespace deleted!",
        }
    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@home.route("/namespaces/get_rights", methods=["POST"])
@login_required
def get_rights():
    post_data = dict(request.json)

    rights = (
        db.session.query(namespaces.P_claim, namespaces.G_claim, namespaces.O_claim)
        .filter(namespaces.id == post_data["id"])
        .all()
    )

    ret_dict = {
        "P_claim": rights[0].P_claim,
        "G_claim": rights[0].G_claim,
        "O_claim": rights[0].O_claim,
    }

    return ret_dict


def parse_claim(claimlist, post_data):

    if all(item in post_data.keys() for item in claimlist):
        claim = "FULL"
    elif any(item in post_data.keys() for item in claimlist):
        if claimlist[0] in post_data.keys():
            claim = "READ"
        elif claimlist[1] in post_data.keys():
            claim = "WRITE"
    else:
        claim = "NONE"

    return claim


@home.route("/namespaces/set_rights", methods=["POST"])
@login_required
def set_rights():

    post_data = dict(request.json)

    post_data["form_data"] = dict(post_data["form_data"])

    try:
        pers_claim = parse_claim(["P_pull", "P_push"], post_data["form_data"])
        group_claim = parse_claim(["G_pull", "G_push"], post_data["form_data"])
        other_claim = parse_claim(["O_pull", "O_push"], post_data["form_data"])

        the_ns = namespaces.query.filter(namespaces.id == post_data["id"]).first()

        the_ns.P_claim = pers_claim
        the_ns.G_claim = group_claim
        the_ns.O_claim = other_claim
        the_ns.updated = int(time.time())

        db.session.add(the_ns)
        db.session.commit()

        total_namespaces = get_total_namespaces()

        return {
            "namespace_data": render_template(
                "partials/namespace_list.html",
                header="Namespace",
                namespaces=total_namespaces,
            ),
            "status": msg_status.OK,
            "msg": "Namespace rights set!",
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@home.route("/namespaces/get_user_list", methods=["POST"])
@login_required
def get_user_list():
    post_data = dict(request.json)

    all_users = (
        users.query.filter(
            users.id.notin_(
                db.session.query(namespacemembers.userid)
                .filter(namespacemembers.namespaceid == int(post_data["id"]))
                .all()
            )
        )
        .filter(
            users.id.notin_(
                db.session.query(namespaces.owner)
                .filter(namespaces.id == int(post_data["id"]))
                .all()
            )
        )
        .all()
    )

    userdetails = [
        {
            "value": x.id,
            "name": x.username,
            "avatar": "/avatars/{}".format(x.avatar_l),
            "email": x.email,
        }
        for x in all_users
    ]

    return jsonify({"user_list": userdetails})


@home.route("/namespaces/get_assigned_users", methods=["POST"])
@login_required
def get_assigned_users():
    post_data = dict(request.json)

    all_userids = (
        db.session.query(namespacemembers.userid)
        .filter(namespacemembers.namespaceid == int(post_data["id"]))
        .all()
    )

    all_userids = [x[0] for x in all_userids]

    all_users = (
        users.query.filter(users.id.in_(all_userids))
        .filter(
            users.id.notin_(
                db.session.query(namespaces.owner)
                .filter(namespaces.id == int(post_data["id"]))
                .all()
            )
        )
        .all()
    )

    return jsonify([x.user_to_dict() for x in all_users])


@home.route("/namespaces/set_user_list", methods=["POST"])
@login_required
def set_user_list():
    post_data = dict(request.json)

    if post_data["data"] != "":
        post_data["data"] = ast.literal_eval(post_data["data"])

        if isinstance(post_data["data"], list):
            for each in post_data["data"]:
                db.session.add(
                    namespacemembers(
                        namespaceid=post_data["namespace_id"], userid=each["value"]
                    )
                )

            db.session.commit()

            return {
                "status": msg_status.OK,
                "msg": "Users assigned!",
            }

        else:
            return jsonify(
                {
                    "status": msg_status.NOK,
                    "msg": "The provided data is not the correct type, expected list got {}".format(
                        type(post_data["data"])
                    ),
                }
            )
    return "Nothing to save..."


@home.route("/namespaces/del_user", methods=["POST"])
@login_required
def del_user():
    post_data = dict(request.json)

    try:
        namespacemembers.query.filter(namespacemembers.userid == post_data["userid"]).delete()

        db.session.commit()

        return {
            "status": msg_status.OK,
            "msg": "User assignment deleted!",
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )
