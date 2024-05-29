from django import template

register = template.Library()

@register.filter(name='modulo_plus_one')
def modulo_plus_one(value, arg):
    return value % arg + 1
