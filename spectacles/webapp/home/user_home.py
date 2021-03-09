import logging
import os

from flask import (
    render_template,
    current_app,
    request,
    session,
    url_for,
    redirect,
    flash,
)
from flask_login import login_required, current_user

from spectacles.webapp.app.models import users
from spectacles.webapp.auth.permissions import user_required
from spectacles.webapp.run import avatars, db
from . import home
from ..auth.forms import ChangePasswordForm
from ...helpers.app_logger import AppLogger

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)


@home.route("/user_profile")
@login_required
@user_required
def user_home():

    password_form = ChangePasswordForm()

    return render_template(
        "/pages/user_profile.html",
        header="User profile {}".format(current_user.username.upper()),
        password_form=password_form,
    )


@home.route("/avatars/upload", methods=["POST"])
@login_required
def upload_avatar():

    f = request.files.get("filename")

    if f.content_type == "image/png":
        raw_filename = avatars.save_avatar(f)
        session["raw_filename"] = raw_filename

        return render_template("pages/crop_pic.html", header="Crop profile picture",)
    else:
        flash(
            "Please don't upload anything other then PNG images smaller then 1MB in size.", "danger"
        )
        return redirect(url_for("home.user_home"))


@home.route("/avatars/save_crop", methods=["POST"])
@login_required
def save_cropped():
    x = request.form.get("x")
    y = request.form.get("y")
    w = request.form.get("w")
    h = request.form.get("h")
    filenames = avatars.crop_avatar(session["raw_filename"], x, y, w, h)

    cur_user = users.query.filter_by(id=current_user.id).first()

    os.remove(os.path.join(current_app.config["AVATARS_SAVE_PATH"], cur_user.avatar_s))
    os.remove(os.path.join(current_app.config["AVATARS_SAVE_PATH"], cur_user.avatar_m))
    os.remove(os.path.join(current_app.config["AVATARS_SAVE_PATH"], cur_user.avatar_l))

    cur_user.avatar_s = filenames[0]
    cur_user.avatar_m = filenames[1]
    cur_user.avatar_l = filenames[2]

    db.session.add(cur_user)
    db.session.commit()

    os.remove(
        os.path.join(current_app.config["AVATARS_SAVE_PATH"], session["raw_filename"])
    )

    return redirect(url_for("home.user_home"))


@home.route("/user/settings/changepw", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    cur_user = users.query.filter_by(id=current_user.id).first()

    if form.validate_on_submit():

        cur_user.hash_password(form.password.data)

        db.session.add(cur_user)
        db.session.commit()

        return redirect(url_for("auth.logout"))

    return redirect(url_for("home.user_home"))
