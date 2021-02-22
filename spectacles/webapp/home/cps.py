import hashlib

from jinja2 import evalcontextfilter

from . import home
from ..admin import admin


@evalcontextfilter
@home.app_template_filter()
@admin.app_template_filter()
def md5(eval_ctx, value):
    return hashlib.md5(value.encode("utf-8")).hexdigest()[:6]
