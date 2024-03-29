import logging

from flask import redirect, url_for, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash

from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import users
from spectacles.webapp.config import Config
from spectacles.webapp.run import login_manager
from . import auth
from .forms import LoginForm

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

    if config.OPENID_LOGIN:
        try:
            from .openid_login import oidc_logout

            oidc_logout()
        except ImportError:
            pass
        except TypeError:
            pass

    if config.PORTAL_URL is not None:
        return redirect(config.PORTAL_URL)
    else:
        # Redirect to login page
        return redirect(url_for("auth.func_login"))


def verify_password(password, password_hash):
    """
    Method to verify the password against the stored password hash
    """
    return check_password_hash(password_hash, password)


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
