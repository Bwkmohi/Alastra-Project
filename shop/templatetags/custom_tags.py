from django import template

register = template.Library()

@register.filter
def to(value):
    return range(value)
