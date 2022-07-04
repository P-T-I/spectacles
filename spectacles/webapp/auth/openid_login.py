import random
import time

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
    group = None

    info = oidc.user_getinfo(["trigram", "client_roles", "realm_roles", "groups"])

    username = info.get("trigram", None)

    client_roles = info.get("client_roles")

    try:
        for each in client_roles:
            if each.startswith("grp_"):
                role = each[4:]
            else:
                group = each.title()
    except TypeError:
        oidc_logout()
        abort(401)

    if role is None or group is None or username is None:
        oidc_logout()
        abort(401)

    account = users.query.filter_by(username=username).first()

    if account:
        # Check role and group accordingly; alter when needed and save to backend
        if account.role != role:
            account.role = role

        if len(account.group_member) != 0:
            # already member of a group; check, alter when needed and save to backend
            group_memb = account.group_member[0]

            if group_memb.group.name != group:
                # not yet in group; fetching group id
                new_group = groups.query.filter_by(name=group).first()
                if new_group:
                    # existing group
                    group_id = new_group.id
                else:
                    # non-existing group
                    new_group = groups(name=group, created=int(time.time()))
                    db.session.add(new_group)
                    db.session.commit()

                    group_id = new_group.id

                group_memb.userid = group_id
                db.session.add(group_memb)
                db.session.commit()

        else:
            # not yet in group; fetching group id
            new_group = groups.query.filter_by(name=group).first()
            if new_group:
                # exsting group
                group_id = new_group.id
            else:
                # non-existing group
                new_group = groups(name=group, created=int(time.time()))
                db.session.add(new_group)
                db.session.commit()

                group_id = new_group.id

            db.session.add(groupmembers(groupid=group_id, userid=account.id))
            db.session.commit()

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
        new_group = groups.query.filter_by(name=group).first()
        if new_group:
            # existing group
            group_id = new_group.id
        else:
            # non-existing group
            new_group = groups(name=group, created=int(time.time()))
            db.session.add(new_group)
            db.session.commit()

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

        db.session.add(groupmembers(groupid=group_id, userid=newuser.id))
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
