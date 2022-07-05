import random

import requests
from flask import redirect, url_for, abort
from flask_login import login_user

from spectacles.webapp.app.models import users, groups, groupmembers
from spectacles.webapp.run import db, oidc
from . import auth


@auth.route("/oidc_login")
@oidc.require_login
def oidc_login():
    role = None
    group_id = None

    info = oidc.user_getinfo(["trigram", "client_roles", "realm_roles", "groups"])

    username = info.get("trigram", None)

    username = username.lower()

    client_roles = info.get("client_roles")

    try:
        for each in client_roles:
            if each.startswith("grp_"):
                role = each[4:]
    except TypeError:
        oidc_logout()
        abort(401)

    if role is None or username is None:
        oidc_logout()
        abort(401)

    account = users.query.filter_by(username=username).first()

    if account:
        # Check role and group accordingly; alter when needed and save to backend
        if account.role != role:
            account.role = role

        db.session.add(account)
        db.session.commit()

        # password validation is done by oidc; just log the user in
        login_user(account)
        return redirect(url_for("home.index"))
    else:
        # nobody found; create user account; set keycloak rights and groups and log the user in
        newuser = users()

        newuser.username = username.upper()
        newuser.email = ""
        newuser.role = role

        # not yet in group; fetching group id
        new_group = groups.query.filter_by(name=role).first()
        if new_group:
            # existing group
            group_id = new_group.id

        # this account is created from openid; generate random password...
        chars = (
            "abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVXYZ"
            "0123456789"
            "#()^[]-_*%&=+/"
        )

        newuser.password = "".join(
            [random.SystemRandom().choice(chars) for _ in range(50)]
        )

        newuser.generate_avatar()

        db.session.add(newuser)
        db.session.commit()

        if group_id is not None:
            db.session.add(groupmembers(groupid=group_id, userid=newuser.id))
            db.session.commit()

        login_user(newuser)
        return redirect(url_for("home.index"))


def oidc_logout():

    with requests.session() as session:

        if oidc is not None:
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
