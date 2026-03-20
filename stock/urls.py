"""
stock/urls.py
Routes URL pour l'application de gestion de stock matériel
Monnaie : MRU (Ouguiya mauritanienne)
"""

from django.urls import path
from . import views

# Namespace pour éviter les conflits de noms d'URL
app_name = 'stock'

urlpatterns = [
    # ===========================
    # 🔐 AUTHENTIFICATION
    # ===========================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ===========================
    # 🏠 TABLEAU DE BORD (Accueil)
    # ===========================
    path('', views.dashboard, name='dashboard'),
    
    # ===========================
    # 📦 PRODUITS - CRUDP (Admin uniquement)
    # ===========================
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produit/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produit/<int:id>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('produit/<int:id>/supprimer/', views.supprimer_produit, name='supprimer_produit'),
    
    # ===========================
    # 📥 ENTRÉES DE STOCK (Admin uniquement)
    # ===========================
    path('entree/', views.ajouter_entree, name='entree'),
    
    # ===========================
    # 📤 VENTES / SORTIES (Admin + Vendeurs 1-4)
    # ===========================
    path('vente/', views.faire_vente, name='vente'),
    path('vente/<int:id>/imprimer/', views.imprimer_vente, name='imprimer_vente'),
    
    # ===========================
    # 📊 EXISTANT & STOCK CRITIQUE
    # ===========================
    path('stock/critique/', views.rapport_stock_critique, name='rapport_stock_critique'),
    
    # ===========================
    # 🕐 TRAÇABILITÉ & HISTORIQUE (Temps réel)
    # ===========================
    path('historique/', views.historique, name='historique'),
    path('historique/imprimer/', views.imprimer_historique, name='imprimer_historique'),
    
    # ===========================
    # 📈 RAPPORTS
    # ===========================
    path('rapport/ventes/', views.rapport_ventes, name='rapport_ventes'),
    path('rapport/entrees/', views.rapport_entrees, name='rapport_entrees'),
]