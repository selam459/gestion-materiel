"""
stock/templatetags/math_extras.py
Filtres mathématiques pour les templates
"""

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplie deux valeurs : {{ value|multiply:arg }}"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0