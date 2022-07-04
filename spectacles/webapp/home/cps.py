import hashlib

from jinja2 import pass_eval_context

from . import home
from ..admin import admin


@pass_eval_context
@home.app_template_filter()
@admin.app_template_filter()
def md5(eval_ctx, value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()[:6]

