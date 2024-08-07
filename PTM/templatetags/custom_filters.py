from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.html import escape
register = template.Library()

@register.filter(name='modulo_plus_one')
def modulo_plus_one(value, arg):
    return value % arg + 1

@register.filter
def absolute_url(request, path):
    return request.build_absolute_uri(path)

@register.filter(name='strip_html')
def strip_html_tags(value):
    return strip_tags(value)

@register.filter(name='truncate_with_more')
def truncate_with_more(value, max_length=100):
    if len(value) <= max_length:
        return escape(value)
    truncated = escape(value[:max_length].rsplit(' ', 1)[0])
    return mark_safe(f'{truncated}... <a href="#" class="read-more" data-full-text="{escape(value)}">Read More</a>')