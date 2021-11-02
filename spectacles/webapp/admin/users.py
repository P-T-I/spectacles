import logging
import time

from flask import render_template, url_for, redirect, request, jsonify
from flask_login import login_required, current_user

from spectacles.webapp.app.models import users, groupmembers, groups
from spectacles.webapp.auth.forms import RegistrationForm
from spectacles.webapp.run import db
from . import admin
from ..auth.permissions import admin_required
from ..helpers.constants.common import msg_status, action_types
from ...helpers.activity_tracker import ActivityTracker
from ...helpers.app_logger import AppLogger

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)

activity_track = ActivityTracker(action_type=action_types.USER)


@admin.route("/users")
@login_required
@admin_required
def get_users():

    total_users = users.query.filter().all()

    return render_template("pages/users.html", header="Users", users=total_users)


@admin.route("/users/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_users():

    form = RegistrationForm()

    if form.validate_on_submit():

        newuser = users(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            created=int(time.time()),
        )

        newuser.generate_avatar()

        db.session.add(newuser)
        db.session.commit()
        activity_track.success(
            "User {} added: {}".format(current_user.username, newuser.username)
        )

        return redirect(url_for("admin.get_users"))

    else:
        return render_template("pages/users.html", header="Users", form=form)


@admin.route("/users/delete", methods=["POST"])
@login_required
@admin_required
def del_users():

    post_data = dict(request.json)

    my_user = users.query.filter_by(id=post_data["id"]).first()

    found_username = my_user.username

    try:
        # catch to prevent deletion of first entered admin
        if my_user.status != 99:
            users.query.filter_by(id=post_data["id"]).delete()
            db.session.commit()
            activity_track.danger(
                "User {} deleted: {}".format(current_user.username, found_username)
            )

        total_users = users.query.filter().all()

        return {
            "user_data": render_template(
                "partials/user_list.html", header="Users", users=total_users
            ),
            "status": msg_status.OK,
            "msg": "User {} deleted!".format(found_username),
        }
    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@admin.route("/users/set_admin", methods=["POST"])
@login_required
@admin_required
def set_admin_users():

    post_data = dict(request.json)

    logger.info("set_admin_users Post_data received: {}".format(post_data))

    try:
        my_user = users.query.filter_by(id=post_data["id"]).first()

        if my_user.status != 99:
            if post_data["is_admin"]:
                my_user.role = "admin"

                myadmin = groups.query.filter_by(name="admin").first()

                gm = groupmembers()
                gm.groupid = myadmin.id
                gm.userid = my_user.id
                db.session.add(gm)

            else:
                my_user.role = "user"

            db.session.add(my_user)
            db.session.commit()

            total_users = users.query.filter().all()

            return jsonify(
                {
                    "user_data": render_template(
                        "partials/user_list.html", header="Users", users=total_users
                    ),
                    "status": msg_status.OK,
                    "msg": "User {} set to role: {}".format(
                        my_user.username, my_user.role
                    ),
                }
            )
        else:
            return jsonify(
                {
                    "status": msg_status.NOK,
                    "msg": "This user is the first entered admin user and cannot be removed as admin!",
                }
            )
    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )


@admin.route("/users/del_group", methods=["POST"])
@login_required
@admin_required
def del_group():
    post_data = dict(request.json)

    try:
        groupmembers.query.filter(
            groupmembers.id == post_data["groupmemberid"]
        ).delete()
        db.session.commit()

        total_users = users.query.filter().all()

        return {
            "user_data": render_template(
                "partials/user_list.html", header="Users", users=total_users
            ),
            "status": msg_status.OK,
            "msg": "Group membership deleted!",
        }
    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )
