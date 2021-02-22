from flask import render_template

from . import home
from ..app.models import users


@home.route("/users")
def get_users():

    total_users = users.query.filter().all()

    return render_template(
        "pages/users.html", header="Users", users=total_users
    )
