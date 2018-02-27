from django import template

register = template.Library()

@register.filter
def change_dot_comma(value):
    value = str(value).replace(',', '.')
    return value