from atexit import register
import markdown

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def render_markdown(value):

    html = markdown.markdown(
        value,
        extensions=["fenced_code"]
    )

    return mark_safe(html)