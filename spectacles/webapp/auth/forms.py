import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    InputRequired,
    ValidationError,
    DataRequired,
)

from spectacles.webapp.app.models import users


class LoginForm(FlaskForm):
    username = StringField(
        "username", validators=[InputRequired()], render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        "password", validators=[InputRequired()], render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Login")


def validate_username(form, field):
    user = users.query.filter_by(username=field.data).first()
    if user or field.data.lower() == "spectacles":
        raise ValidationError({"Username is already in use": []})


def validate_password(form, field):
    if field.data != form.confirm_password.data:
        raise ValidationError({"Passwords do not match": []})


def password_check(form, field):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(field.data) < 8

    # searching for digits
    digit_error = re.search(r"\d", field.data) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", field.data) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", field.data) is None

    # searching for symbols
    symbol_error = (
        re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', field.data) is None
    )

    # overall result
    password_ok = not (
        length_error
        or digit_error
        or uppercase_error
        or lowercase_error
        or symbol_error
    )

    if password_ok is False:
        raise ValidationError(
            {
                "The provided password does not meet the following criteria:": [
                    "8 characters length or more",
                    "1 digit or more",
                    "1 symbol or more",
                    "1 uppercase letter or more",
                    "1 lowercase letter or more",
                ]
            }
        )


class RegistrationForm(FlaskForm):
    """
    Form for users to create new account
    """

    username = StringField(
        "username",
        validators=[validate_username],
        render_kw={"placeholder": "Username"},
    )
    email = EmailField(
        "email",
        validators=[DataRequired()],
        render_kw={"placeholder": "email address"},
    )
    password = PasswordField(
        "password",
        validators=[validate_password, password_check],
        render_kw={"placeholder": "Password"},
    )
    confirm_password = PasswordField(
        "Confirm password", render_kw={"placeholder": "Retype password"}
    )

    submit = SubmitField("Register")
    save = SubmitField("Save")
