"""
stock/templatetags/user_extras.py
Filtres personnalisés pour vérifier les permissions utilisateur
"""

from django import template

register = template.Library()

@register.filter
def is_in_group(user, group_name):
    """
    Vérifie si un utilisateur appartient à un groupe
    Usage dans le template : {{ user|is_in_group:"Admin" }}
    """
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()