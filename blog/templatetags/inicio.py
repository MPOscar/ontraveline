from django import template

register = template.Library()

@register.filter
def inicio(value, cantidad_caracteres):
   return value[:cantidad_caracteres]