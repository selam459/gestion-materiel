from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplie deux nombres."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0  # ou '' selon le contexte