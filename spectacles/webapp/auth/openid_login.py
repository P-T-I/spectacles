import random

import requests
from flask import redirect, url_for, request
from flask_login import login_user

from spectacles.webapp.app.models import users
from spectacles.webapp.run import db, oidc
from . import auth


@auth.route("/oidc_login")
@oidc.require_login
def oidc_login():
    info = oidc.user_getinfo(["preferred_username", "sub"])

    username = info.get("preferred_username")

    account = users.query.filter_by(username=username).first()

    if account:
        # password validation is done by oidc; just log the user in
        login_user(account)
        return redirect(url_for("home.index"))
    else:
        # nobody found; create user account with least privileges and log the user in
        newuser = users()

        newuser.username = username
        newuser.email = ""

        # this account is created from openid; generate random password...
        chars = (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVXYZ"
            "0123456789"
            "#()^[]-_*%&=+/"
        )

        newuser.password = "".join(
            [random.SystemRandom().choice(chars) for i in range(50)]
        )

        newuser.generate_avatar()

        db.session.add(newuser)
        db.session.commit()

        login_user(newuser)
        return redirect(url_for("home.index"))


def oidc_logout():

    with requests.session() as session:

        headers = {
            "Authorization": f"Bearer {oidc.get_access_token()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "client_id": f"{oidc.client_secrets.get('client_id')}",
            "client_secret": f"{oidc.client_secrets.get('client_secret')}",
            "refresh_token": f"{oidc.get_refresh_token()}",
        }

        session.post(
            url=f"{oidc.client_secrets.get('issuer')}/protocol/openid-connect/logout",
            data=data,
            headers=headers,
            verify=False,
        )

    oidc.logout()
