import ast
import logging
import time

from flask import render_template, url_for, redirect, request, jsonify
from flask_login import login_required, current_user

from spectacles.webapp.app.models import groups, users, groupmembers
from spectacles.webapp.run import db
from . import admin
from .forms import GroupForm
from ..auth.permissions import admin_required
from ..helpers.constants.common import msg_status, action_types
from ...helpers.activity_tracker import ActivityTracker
from ...helpers.app_logger import AppLogger

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)

activity_track = ActivityTracker(action_type=action_types.GROUP)


@admin.route("/groups")
@login_required
@admin_required
def get_groups():

    total_groups = groups.query.filter().all()

    return render_template("pages/groups.html", header="Groups", groups=total_groups)


@admin.route("/groups/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_groups():

    form = GroupForm()

    if form.validate_on_submit():

        # Create variables for easy access
        newgroup = groups()

        newgroup.name = form.name.data
        newgroup.description = form.description.data
        newgroup.created = int(time.time())

        db.session.add(newgroup)
        db.session.commit()
        activity_track.success(
            "User {} added group: {}".format(current_user.username, newgroup.name)
        )

        return redirect(url_for("admin.get_groups"))

    else:
        return render_template("pages/groups.html", header="Groups", form=form)


@admin.route("/groups/delete", methods=["POST"])
@login_required
@admin_required
def del_groups():

    post_data = dict(request.json)

    my_group = groups.query.filter_by(id=post_data["id"]).first()

    found_name = my_group.name

    try:
        # catch to prevent deletion of admin group
        if my_group.name != "admin":
            groups.query.filter_by(id=post_data["id"]).delete()
            db.session.commit()
            activity_track.danger(
                "User {} deleted group: {}".format(current_user.username, found_name)
            )

        total_groups = groups.query.filter().all()

        return {
            "group_data": render_template(
                "partials/group_list.html", header="Groups", groups=total_groups
            ),
            "status": msg_status.OK,
            "msg": "Group {} deleted!".format(found_name),
        }
    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@admin.route("/groups/get_user_list", methods=["POST"])
@login_required
@admin_required
def get_user_list():
    post_data = dict(request.json)

    group_id = post_data["id"]

    all_users = users.query.filter(
        users.id.notin_(
            db.session.query(groupmembers.userid)
            .filter(groupmembers.groupid == int(group_id))
            .all()
        )
    ).all()

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


@admin.route("/groups/set_user_list", methods=["POST"])
@login_required
@admin_required
def set_user_list():
    post_data = dict(request.json)

    post_data["data"] = ast.literal_eval(post_data["data"])

    if isinstance(post_data["data"], list):
        for each in post_data["data"]:
            db.session.add(
                groupmembers(groupid=post_data["group_id"], userid=each["value"])
            )

        db.session.commit()

        total_groups = groups.query.filter().all()

        return {
            "group_data": render_template(
                "partials/group_list.html", header="Groups", groups=total_groups
            ),
            "status": msg_status.OK,
            "msg": "Group members assigned!",
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


@admin.route("/groups/del_groupmember", methods=["POST"])
@login_required
@admin_required
def del_groupmember():
    post_data = dict(request.json)

    try:
        groupmembers.query.filter(
            groupmembers.id == post_data["groupmemberid"]
        ).delete()
        db.session.commit()

        total_groups = groups.query.filter().all()

        return {
            "group_data": render_template(
                "partials/group_list.html", header="Groups", groups=total_groups
            ),
            "status": msg_status.OK,
            "msg": "Group member deleted!",
        }
    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )
