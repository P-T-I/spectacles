from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, ValidationError, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired

from spectacles.webapp.app.models import groups


def validate_groupname(form, field):
    user = groups.query.filter_by(name=field.data).first()
    if user:
        raise ValidationError({"Groupname is already in use": []})


class GroupForm(FlaskForm):
    name = StringField(
        "name", validators=[validate_groupname], render_kw={"placeholder": "Group name"}
    )
    description = TextAreaField(
        "description",
        render_kw={"placeholder": "Description (optional)", "rows": 10, "cols": 1},
    )
    save = SubmitField("Save")


class RegistryForm(FlaskForm):
    uri = StringField(
        "uri", validators=[DataRequired()], render_kw={"placeholder": "Registry domain/ip:port"}
    )
    service_name = StringField(
        "service_name", validators=[DataRequired()], render_kw={'disabled': 'disabled', "placeholder": "Service name..."}
    )
    ssl = BooleanField("ssl")

    test = SubmitField("Test")
    save = SubmitField("Save", render_kw={'disabled': 'disabled'})
