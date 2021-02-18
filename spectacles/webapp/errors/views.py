from flask import render_template
from flask_login import current_user

from . import errors


@errors.route("/50x")
def user_home():
    return (
        render_template(
            "errors/500.html",
            header="Internal Server Error",
            authenticated=current_user.is_authenticated,
            error=True,
        ),
        500,
    )
