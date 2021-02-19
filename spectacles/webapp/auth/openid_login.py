import random

from flask import redirect, url_for
from flask_login import login_user

from spectacles.webapp.app.models import users
from spectacles.webapp.run import db, oidc
from . import auth


@auth.route("/oidc_login")
@oidc.require_login
def oidc_login():
    info = oidc.user_getinfo(["preferred_username", "sub"])

    username = info.get("preferred_username")

    account = users.query.filter_by(name=username).first()

    if account:
        # password validation is done by oidc; just log the user in
        login_user(account)
        return redirect(url_for("home.index"))
    else:
        # nobody found; create user account with least privileges and log the user in
        newuser = users()

        newuser.name = username
        newuser.fullname = ""
        newuser.email = ""
        newuser.phone = ""

        # this account is created from openid; generate random password...
        chars = (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVXYZ"
            "0123456789"
            "#()^[]-_*%&=+/"
        )

        newuser.hash_password(
            "".join([random.SystemRandom().choice(chars) for i in range(50)])
        )

        newuser.generate_avatar()

        db.session.add(newuser)
        db.session.commit()

        usersettings = settingsmembers()

        usersettings.userid = newuser.id

        usersettings.planningemails = 1
        usersettings.planningnotifications = 1
        usersettings.eventemails = 1
        usersettings.eventnotifications = 1
        usersettings.theme = 0

        db.session.add(usersettings)
        db.session.commit()

        login_user(newuser)
        return redirect(url_for("home.index"))


def oidc_logout():
    oidc.logout()
