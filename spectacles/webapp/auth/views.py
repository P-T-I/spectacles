import logging
import time

from flask import redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash

from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import (
    users,
    groups,
    groupmembers,
    namespaces,
    namespacemembers,
)
from spectacles.webapp.config import Config
from spectacles.webapp.run import login_manager, db
from . import auth
from .forms import LoginForm, RegistrationForm

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)

config = Config()


@login_manager.user_loader
def load_user(user_id):

    user = users.query.filter_by(id=user_id).first()

    return user


@auth.route("/logout")
@login_required
def logout():
    logout_user()

    try:
        from .openid_login import oidc_logout

        oidc_logout()
    except ImportError:
        pass

    # Redirect to login page
    return redirect(url_for("auth.func_login"))


def verify_password(password, password_hash):
    """
    Method to verify the password against the stored password hash
    """
    return check_password_hash(password_hash, password)


@auth.route("/register", methods=["GET", "POST"])
def register():

    form = RegistrationForm()
    if form.validate_on_submit():

        # check if this is the first account to created; thus the admin....
        usercount = users.query.filter().count()

        # Create variables for easy access
        newuser = users(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            created=int(time.time()),
        )

        if usercount is None or usercount == 0:
            newuser.role = "admin"
            newuser.status = 99

            # also create admin group
            newgroup = groups()
            newgroup.name = "admin"
            newgroup.description = "Administrator group"
            newgroup.created = int(time.time())
            db.session.add(newgroup)
            db.session.commit()

        newuser.generate_avatar()

        db.session.add(newuser)
        db.session.commit()

        if usercount is None or usercount == 0:
            # add this admin to admin group
            newgroupmember = groupmembers()
            newgroupmember.groupid = newgroup.id
            newgroupmember.userid = newuser.id
            db.session.add(newgroupmember)
            db.session.commit()

        login_user(newuser)

        return redirect(url_for("home.index"))
    else:

        return render_template("pages/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def func_login():

    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = LoginForm()
    if form.validate_on_submit():

        # Check if account exists
        account = users.query.filter_by(username=form.username.data).first()

        if account and account.verify_password(form.password.data):
            login_user(account)

            return redirect(url_for("home.index"))
        else:
            msg = "Incorrect username/password!"
            return render_template(
                "pages/login.html", form=form, msg=msg, openid=config.OPENID_LOGIN
            )

    return render_template("pages/login.html", form=form, openid=config.OPENID_LOGIN)
