from flask import render_template, url_for, redirect, request
from flask_login import login_required

from spectacles.webapp.app.models import users
from spectacles.webapp.auth.forms import RegistrationForm
from spectacles.webapp.run import db
from . import admin
from ..auth.permissions import admin_required


@admin.route("/users")
@login_required
@admin_required
def get_users():

    total_users = users.query.filter().all()

    return render_template(
        "pages/users.html", header="Users", users=total_users
    )


@admin.route("/users/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_users():

    form = RegistrationForm()

    if form.validate_on_submit():

        # Create variables for easy access
        newuser = users()

        newuser.username = form.username.data
        newuser.email = form.email.data

        newuser.hash_password(form.password.data)

        newuser.generate_avatar()

        db.session.add(newuser)
        db.session.commit()

        return redirect(url_for("home.get_users"))

    else:
        return render_template(
            "pages/users.html", header="Users", form=form
        )


@admin.route("/users/delete", methods=["POST"])
@login_required
@admin_required
def del_users():

    post_data = dict(request.json)

    users.query.filter_by(id=post_data["id"]).delete()
    db.session.commit()

    total_users = users.query.filter().all()

    return render_template(
        "partials/user_list.html", header="Users", users=total_users
    )
