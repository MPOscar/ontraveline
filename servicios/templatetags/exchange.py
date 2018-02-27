from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def exchange(value, rate):
    return Decimal(value) * Decimal(rate)