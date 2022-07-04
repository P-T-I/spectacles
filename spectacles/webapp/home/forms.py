from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    ValidationError,
    TextAreaField,
    SubmitField,
    SelectField,
)

from spectacles.webapp.app.models import namespaces


def validate_namespacename(form, field):
    user = namespaces.query.filter_by(name=field.data).first()
    if user:
        raise ValidationError({"Groupname is already in use": []})


class NamespaceForm(FlaskForm):
    registry = SelectField("type", render_kw={"placeholder": "Registry"})
    name = StringField(
        "name",
        validators=[validate_namespacename],
        render_kw={"placeholder": "Namespace name"},
    )
    description = TextAreaField(
        "description",
        render_kw={"placeholder": "Description (optional)", "rows": 2, "cols": 1},
    )
    save = SubmitField("Save")
