import logging
import time

from flask import render_template, url_for, redirect, request, jsonify
from flask_login import login_required

from spectacles.webapp.app.models import groups
from spectacles.webapp.run import db
from . import admin
from .forms import GroupForm
from ..auth.permissions import admin_required
from ..helpers.constants.common import msg_status
from ...helpers.app_logger import AppLogger

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


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

        total_groups = groups.query.filter().all()

        return {"group_data": render_template("partials/group_list.html", header="Groups", groups=total_groups),
                "status": msg_status.OK,
                "msg": "Group {} deleted!".format(found_name)}
    except Exception as err:
        return jsonify(
            {"status": msg_status.NOK, "msg": "Error encountered: {}".format(err)}
        )
