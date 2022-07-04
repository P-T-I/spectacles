import logging
import time

from flask import redirect, url_for, render_template
from flask_login import login_user

from spectacles.helpers.app_logger import AppLogger
from spectacles.webapp.app.models import users, groups, groupmembers
from spectacles.webapp.config import Config
from spectacles.webapp.run import db
from . import auth
from .forms import RegistrationForm

logging.setLoggerClass(AppLogger)

logger = logging.getLogger(__name__)

config = Config()


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
