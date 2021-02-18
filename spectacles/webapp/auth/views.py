import logging

from flask import redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash

from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import users
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


@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    return render_template("pages/forgot_password.html")


@auth.route("/register", methods=["GET", "POST"])
def register():

    form = RegistrationForm()
    if form.validate_on_submit():

        # Create variables for easy access
        newuser = users()

        newuser.name = form.name.data
        newuser.fullname = form.fullname.data
        newuser.email = form.email.data
        newuser.phone = form.phone.data

        newuser.hash_password(form.password.data)

        newuser.generate_avatar()

        db.session.add(newuser)
        db.session.commit()
        msg = "You have successfully registered!"

        # Show registration form with message (if any)
        return render_template("pages/register.html", form=form, msg=msg)
    else:
        return render_template("pages/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def func_login():

    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = LoginForm()
    if form.validate_on_submit():

        # error output message
        msg = ""
        # Check if "username" and "password" POST requests exist (user submitted form)

        # Check if account exists using MySQL
        account = users.query.filter_by(name=form.username.data).first()

        if account and verify_password(form.password.data, account.password):
            login_user(account)

            return redirect(url_for("home.index"))
        else:
            msg = "Incorrect username/password!"
            return render_template(
                "pages/login.html", form=form, msg=msg, openid=config.OPENID_LOGIN
            )

    return render_template("pages/login.html", form=form, openid=config.OPENID_LOGIN)
