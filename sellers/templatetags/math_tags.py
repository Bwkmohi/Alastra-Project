from django import template
register = template.Library()

@register.filter
def div(value, arg):
    try:
        return (value / arg) * 100 if arg != 0 else 0
    except:
        return 0
