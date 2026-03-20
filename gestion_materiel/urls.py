"""
gestion_materiel/urls.py
Fichier de configuration des URLs principales du projet
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),
    
    # Inclure TOUTES les URLs de l'application stock
    path('', include('stock.urls', namespace='stock')),
]

# Gestion des fichiers statiques (logo, CSS, etc.) en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)