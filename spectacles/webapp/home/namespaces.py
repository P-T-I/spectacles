import ast
import time

from flask import render_template, request, jsonify, url_for
from flask_login import login_required, current_user

from . import home
from .forms import NamespaceForm
from ..app.models import (
    namespaces,
    namespacemembers,
    namespacegroups,
    groupmembers,
    users,
    groups,
    claims,
    claimsmembers,
    claimsgroups,
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
        total_namespaces = (
            namespaces.query.filter().order_by(namespaces.name.asc()).all()
        )
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
        .filter(users.role != "admin")
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


@home.route("/namespaces/get_group_list", methods=["POST"])
@login_required
def get_group_list():
    post_data = dict(request.json)

    all_groups = (
        groups.query.filter(
            groups.id.notin_(
                db.session.query(namespacegroups.groupid)
                .filter(namespacegroups.namespaceid == int(post_data["id"]))
                .all()
            )
        )
        .filter(groups.name != "admin")
        .all()
    )

    groupdetails = [
        {
            "value": x.id,
            "name": x.name,
            "avatar": url_for("static", filename="images/group_avatar.png"),
        }
        for x in all_groups
    ]

    return jsonify({"group_list": groupdetails})


@home.route("/namespaces/get_assigned_users_groups", methods=["POST"])
@login_required
def get_assigned_users_groups():
    post_data = dict(request.json)

    all_userids = (
        db.session.query(namespacemembers.userid)
        .filter(namespacemembers.namespaceid == int(post_data["id"]))
        .all()
    )

    all_userids = [x.userid for x in all_userids]

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

    all_groupids = (
        db.session.query(namespacegroups.groupid)
        .filter(namespacegroups.namespaceid == int(post_data["id"]))
        .all()
    )

    all_groupids = [x.groupid for x in all_groupids]

    all_groups = groups.query.filter(groups.id.in_(all_groupids)).all()

    ret_data = {
        "users": [x.user_to_dict() for x in all_users],
        "groups": [x.group_dict() for x in all_groups],
    }

    return ret_data


@home.route("/namespaces/set_user_group_list", methods=["POST"])
@login_required
def set_user_list():
    post_data = dict(request.json)

    try:
        if post_data["user_data"] != "":
            post_data["user_data"] = ast.literal_eval(post_data["user_data"])

            if isinstance(post_data["user_data"], list):
                for each in post_data["user_data"]:
                    db.session.add(
                        namespacemembers(
                            namespaceid=post_data["namespace_id"], userid=each["value"]
                        )
                    )

                db.session.commit()

        if post_data["group_data"] != "":
            post_data["group_data"] = ast.literal_eval(post_data["group_data"])

            if isinstance(post_data["group_data"], list):
                for each in post_data["group_data"]:
                    db.session.add(
                        namespacegroups(
                            namespaceid=post_data["namespace_id"], groupid=each["value"]
                        )
                    )

                db.session.commit()

        return {
            "status": msg_status.OK,
            "msg": "Rights assigned!",
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@home.route("/namespaces/del_user", methods=["POST"])
@login_required
def del_user():
    post_data = dict(request.json)

    try:
        namespacemembers.query.filter(
            namespacemembers.userid == post_data["userid"]
        ).filter(namespacemembers.namespaceid == post_data["namespaceid"]).delete()

        db.session.commit()

        return {
            "status": msg_status.OK,
            "msg": "User assignment deleted!",
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@home.route("/namespaces/del_group", methods=["POST"])
@login_required
def del_ns_group():
    post_data = dict(request.json)

    try:
        namespacegroups.query.filter(
            namespacegroups.groupid == post_data["groupid"]
        ).filter(namespacegroups.namespaceid == post_data["namespaceid"]).delete()

        db.session.commit()

        return {
            "status": msg_status.OK,
            "msg": "Group assignment deleted!",
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@home.route("/namespaces/get_custom_assigned_users_groups", methods=["POST"])
@login_required
def get_custom_assigned_users_groups():
    post_data = dict(request.json)

    ns_claims = claims.query.filter(claims.namespaceid == int(post_data["id"])).all()

    if len(ns_claims) == 0:
        all_claims = ["READ", "WRITE", "FULL"]
        for each in all_claims:
            db.session.add(
                claims(
                    claim=each,
                    namespaceid=int(post_data["id"]),
                    created=int(time.time()),
                )
            )
            db.session.commit()

        return {
            "read_users": [],
            "write_users": [],
            "ful_users": [],
            "read_groups": [],
            "write_groups": [],
            "full_groups": [],
        }

    else:

        ret_dict = {}

        for claim in ns_claims:
            if claim.claim == "READ":
                ret_dict["read_users"] = [x.user.user_to_dict() for x in claim.members]
                ret_dict["read_groups"] = [x.group.group_dict() for x in claim.groups]
                ret_dict["read_claim"] = claim.id
            if claim.claim == "WRITE":
                ret_dict["write_users"] = [x.user.user_to_dict() for x in claim.members]
                ret_dict["write_groups"] = [x.group.group_dict() for x in claim.groups]
                ret_dict["write_claim"] = claim.id
            if claim.claim == "FULL":
                ret_dict["full_users"] = [x.user.user_to_dict() for x in claim.members]
                ret_dict["full_groups"] = [x.group.group_dict() for x in claim.groups]
                ret_dict["full_claim"] = claim.id

        return ret_dict


@home.route("/namespaces/get_custom_user_list", methods=["POST"])
@login_required
def get_custom_user_list():
    post_data = dict(request.json)

    ns_claims = claims.query.filter(claims.namespaceid == int(post_data["id"])).all()

    ret_dict = {}

    user_list = []
    for each in ns_claims:
        for x in each.members:
            user_list.append(x.userid)

    for claim in ns_claims:
        if claim.claim == "READ":
            ns_members = [x.userid for x in claim.members]
            all_users = (
                users.query.filter(users.id.notin_(ns_members))
                .filter(
                    users.id.notin_(
                        db.session.query(namespaces.owner)
                        .filter(namespaces.id == int(post_data["id"]))
                        .all()
                    )
                )
                .filter(users.id.notin_(user_list))
                .filter(users.role != "admin")
                .all()
            )

            ret_dict["read_user_list"] = [
                {
                    "value": x.id,
                    "name": x.username,
                    "avatar": "/avatars/{}".format(x.avatar_l),
                    "email": x.email,
                }
                for x in all_users
            ]
        if claim.claim == "WRITE":
            ns_members = [x.userid for x in claim.members]
            all_users = (
                users.query.filter(users.id.notin_(ns_members))
                .filter(
                    users.id.notin_(
                        db.session.query(namespaces.owner)
                        .filter(namespaces.id == int(post_data["id"]))
                        .all()
                    )
                )
                .filter(users.id.notin_(user_list))
                .filter(users.role != "admin")
                .all()
            )

            ret_dict["write_user_list"] = [
                {
                    "value": x.id,
                    "name": x.username,
                    "avatar": "/avatars/{}".format(x.avatar_l),
                    "email": x.email,
                }
                for x in all_users
            ]
        if claim.claim == "FULL":
            ns_members = [x.userid for x in claim.members]
            all_users = (
                users.query.filter(users.id.notin_(ns_members))
                .filter(
                    users.id.notin_(
                        db.session.query(namespaces.owner)
                        .filter(namespaces.id == int(post_data["id"]))
                        .all()
                    )
                )
                .filter(users.id.notin_(user_list))
                .filter(users.role != "admin")
                .all()
            )

            ret_dict["full_user_list"] = [
                {
                    "value": x.id,
                    "name": x.username,
                    "avatar": "/avatars/{}".format(x.avatar_l),
                    "email": x.email,
                }
                for x in all_users
            ]
    return ret_dict


@home.route("/namespaces/get_custom_group_list", methods=["POST"])
@login_required
def get_custom_group_list():
    post_data = dict(request.json)

    ns_claims = claims.query.filter(claims.namespaceid == int(post_data["id"])).all()

    ret_dict = {}

    group_list = []
    for each in ns_claims:
        for x in each.groups:
            group_list.append(x.groupid)

    for claim in ns_claims:
        if claim.claim == "READ":
            ns_members = [x.groupid for x in claim.groups]
            all_groups = (
                groups.query.filter(groups.id.notin_(ns_members))
                .filter(groups.id.notin_(group_list))
                .filter(groups.name != "admin")
                .all()
            )

            ret_dict["read_group_list"] = [
                {
                    "value": x.id,
                    "name": x.name,
                    "avatar": url_for("static", filename="images/group_avatar.png"),
                }
                for x in all_groups
            ]
        if claim.claim == "WRITE":
            ns_members = [x.groupid for x in claim.groups]
            all_groups = (
                groups.query.filter(groups.id.notin_(ns_members))
                .filter(groups.id.notin_(group_list))
                .filter(groups.name != "admin")
                .all()
            )

            ret_dict["write_group_list"] = [
                {
                    "value": x.id,
                    "name": x.name,
                    "avatar": url_for("static", filename="images/group_avatar.png"),
                }
                for x in all_groups
            ]
        if claim.claim == "FULL":
            ns_members = [x.groupid for x in claim.groups]
            all_groups = (
                groups.query.filter(groups.id.notin_(ns_members))
                .filter(groups.id.notin_(group_list))
                .filter(groups.name != "admin")
                .all()
            )

            ret_dict["full_group_list"] = [
                {
                    "value": x.id,
                    "name": x.name,
                    "avatar": url_for("static", filename="images/group_avatar.png"),
                }
                for x in all_groups
            ]

    return ret_dict


@home.route("/namespaces/set_custom_user_group_list", methods=["POST"])
@login_required
def set_custom_user_group_list():
    post_data = dict(request.json)

    def add_claim_members(data_list, claim_id):
        if isinstance(data_list, list):
            for each in data_list:
                db.session.add(
                    claimsmembers(claimsid=int(claim_id), userid=each["value"])
                )

            db.session.commit()

    def add_claim_groups(data_list, claim_id):
        if isinstance(data_list, list):
            for each in data_list:
                db.session.add(
                    claimsgroups(claimsid=int(claim_id), groupid=each["value"])
                )

            db.session.commit()

    try:
        if post_data["read_user_data"] != "":
            post_data["read_user_data"] = ast.literal_eval(post_data["read_user_data"])
            add_claim_members(post_data["read_user_data"], post_data["read_claim"])
        if post_data["read_group_data"] != "":
            post_data["read_group_data"] = ast.literal_eval(
                post_data["read_group_data"]
            )
            add_claim_groups(post_data["read_group_data"], post_data["read_claim"])

        if post_data["write_user_data"] != "":
            post_data["write_user_data"] = ast.literal_eval(
                post_data["write_user_data"]
            )
            add_claim_members(post_data["write_user_data"], post_data["write_claim"])
        if post_data["write_group_data"] != "":
            post_data["write_group_data"] = ast.literal_eval(
                post_data["write_group_data"]
            )
            add_claim_groups(post_data["write_group_data"], post_data["write_claim"])

        if post_data["full_user_data"] != "":
            post_data["full_user_data"] = ast.literal_eval(post_data["full_user_data"])
            add_claim_members(post_data["full_user_data"], post_data["full_claim"])
        if post_data["full_group_data"] != "":
            post_data["full_group_data"] = ast.literal_eval(
                post_data["full_group_data"]
            )
            add_claim_groups(post_data["full_group_data"], post_data["full_claim"])

        return {
            "status": msg_status.OK,
            "msg": "Rights assigned!",
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@home.route("/namespaces/del_claim_user", methods=["POST"])
@login_required
def del_claim_user():
    post_data = dict(request.json)

    try:
        claimsmembers.query.filter(claimsmembers.userid == post_data["userid"]).filter(
            claimsmembers.claimsid == post_data["claimid"]
        ).delete()

        db.session.commit()

        return {
            "status": msg_status.OK,
            "msg": "Group assignment deleted!",
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@home.route("/namespaces/del_claim_group", methods=["POST"])
@login_required
def del_claim_group():
    post_data = dict(request.json)

    try:
        claimsgroups.query.filter(claimsgroups.groupid == post_data["groupid"]).filter(
            claimsgroups.claimsid == post_data["claimid"]
        ).delete()

        db.session.commit()

        return {
            "status": msg_status.OK,
            "msg": "User assignment deleted!",
        }

    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )
