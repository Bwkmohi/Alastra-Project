from django import template

register = template.Library()

@register.filter
def get_item(details, key):
    for item in details:
        if item['key'] == key:
            return item['value']
    return None
