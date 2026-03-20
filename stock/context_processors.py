"""
stock/context_processors.py
Variables globales disponibles dans tous les templates
"""

def user_permissions(request):
    """Ajoute is_admin et is_vendeur au contexte de tous les templates"""
    if not request.user.is_authenticated:
        return {
            'is_admin': False,
            'is_vendeur': False,
        }
    
    return {
        'is_admin': request.user.is_superuser or request.user.groups.filter(name='Admin').exists(),
        'is_vendeur': request.user.is_superuser or request.user.groups.filter(name='Vendeurs').exists(),
    }