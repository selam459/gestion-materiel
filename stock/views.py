"""
stock/views.py
Toutes les vues de l'application de gestion de stock matériel
Monnaie : MRU (Ouguiya mauritanienne)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F, Q
from django.utils import timezone
from datetime import datetime

# Imports des modèles
from .models import Produit, Mouvement, AuditLog


# ===========================
# 🔑 DÉCORATEURS DE PERMISSION (déplacés avant leur utilisation)
# ===========================

def is_admin(user):
    """Vérifie si l'utilisateur est admin"""
    return user.groups.filter(name='Admin').exists() or user.is_superuser

def is_vendeur(user):
    """Vérifie si l'utilisateur est vendeur"""
    return user.groups.filter(name='Vendeurs').exists() or user.is_superuser


# ===========================
# 🔐 FONCTIONS D'AUTHENTIFICATION
# ===========================

def login_view(request):
    """Page de connexion"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Bon retour parmi nous, {user.username} !')
            return redirect('stock:dashboard')
        else:
            messages.error(request, '❌ Identifiants incorrects. Veuillez réessayer.')
    
    return render(request, 'stock/login.html')

def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.info(request, '👋 Vous avez été déconnecté avec succès.')
    return redirect('stock:login')


# ===========================
# 🏠 TABLEAU DE BORD
# ===========================

@login_required
def dashboard(request):
    """Tableau de bord principal - État du stock en temps réel"""
    produits = Produit.objects.all().order_by('nom')
    
    # Calcul de la valeur totale pour chaque produit (en mémoire)
    for p in produits:
        p.montant_total = p.stock_actuel * p.prix_unitaire
    
    # Valeur totale du stock
    total_valeur_stock = sum(p.montant_total for p in produits)
    
    # Produits en stock critique
    produits_critiques = produits.filter(stock_actuel__lte=F('seuil_critique'))
    
    # Derniers mouvements
    derniers_mouvements = Mouvement.objects.all().select_related('produit', 'opere_par').order_by('-date_operation')[:10]
    
    context = {
        'produits': produits,
        'total_valeur': total_valeur_stock,
        'produits_critiques_count': produits_critiques.count(),
        'produits_critiques': produits_critiques,
        'derniers_mouvements': derniers_mouvements,
        'is_admin': is_admin(request.user),
        'total_produits': produits.count(),
    }
    
    return render(request, 'stock/dashboard.html', context)


# ===========================
# 📦 GESTION DES PRODUITS (CRUD - Admin)
# ===========================

@login_required
def liste_produits(request):
    """Liste de tous les produits"""
    if not is_admin(request.user):
        messages.error(request, '⛔ Accès réservé aux administrateurs.')
        return redirect('stock:dashboard')
    
    produits = Produit.objects.all().order_by('nom')
    return render(request, 'stock/liste_produits.html', {'produits': produits})

@login_required
def ajouter_produit(request):
    """Ajouter un nouveau produit"""
    if not is_admin(request.user):
        messages.error(request, '⛔ Accès réservé aux administrateurs.')
        return redirect('stock:dashboard')
    
    if request.method == 'POST':
        try:
            Produit.objects.create(
                nom=request.POST.get('nom'),
                description=request.POST.get('description', ''),
                prix_unitaire=float(request.POST.get('prix_unitaire', 0)),
                seuil_critique=int(request.POST.get('seuil_critique', 5)),
                stock_actuel=int(request.POST.get('stock_initial', 0))
            )
            messages.success(request, f'✅ Produit "{request.POST.get("nom")}" ajouté avec succès !')
            return redirect('stock:liste_produits')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    return render(request, 'stock/produit_form.html', {'action': 'ajouter'})

@login_required
def modifier_produit(request, id):
    """Modifier un produit existant"""
    if not is_admin(request.user):
        messages.error(request, '⛔ Accès réservé aux administrateurs.')
        return redirect('stock:dashboard')
    
    produit = get_object_or_404(Produit, id=id)
    
    # Valeur actuelle du stock (pour affichage)
    produit.valeur_actuelle = produit.stock_actuel * produit.prix_unitaire
    
    if request.method == 'POST':
        try:
            produit.nom = request.POST.get('nom')
            produit.description = request.POST.get('description', '')
            produit.prix_unitaire = float(request.POST.get('prix_unitaire', 0))
            produit.seuil_critique = int(request.POST.get('seuil_critique', 5))
            produit.save()
            messages.success(request, f'✅ Produit "{produit.nom}" modifié avec succès !')
            return redirect('stock:liste_produits')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    return render(request, 'stock/produit_form.html', {
        'action': 'modifier',
        'produit': produit
    })

@login_required
def supprimer_produit(request, id):
    """Supprimer un produit"""
    if not is_admin(request.user):
        messages.error(request, '⛔ Accès réservé aux administrateurs.')
        return redirect('stock:dashboard')
    
    produit = get_object_or_404(Produit, id=id)
    
    if request.method == 'POST':
        nom = produit.nom
        produit.delete()
        messages.success(request, f'✅ Produit "{nom}" supprimé avec succès !')
        return redirect('stock:liste_produits')
    
    return render(request, 'stock/produit_confirm_delete.html', {'produit': produit})


# ===========================
# 📥 ENTRÉES DE STOCK (Admin)
# ===========================

@login_required
def ajouter_entree(request):
    """Enregistrer une entrée de stock"""
    if not is_admin(request.user):
        messages.error(request, '⛔ Accès réservé aux administrateurs.')
        return redirect('stock:dashboard')
    
    if request.method == 'POST':
        try:
            produit_id = request.POST.get('produit')
            quantite = int(request.POST.get('quantite'))
            produit = get_object_or_404(Produit, id=produit_id)
            
            # Mise à jour du stock
            produit.stock_actuel += quantite
            produit.save()
            
            # Créer le mouvement
            Mouvement.objects.create(
                produit=produit,
                type_mouvement='ENTREE',
                quantite=quantite,
                montant_total=quantite * produit.prix_unitaire,
                opere_par=request.user,
                commentaire=request.POST.get('commentaire', '')
            )
            
            # Log d'audit
            AuditLog.objects.create(
                action=f"ENTRÉE: +{quantite} {produit.nom}",
                user=request.user
            )
            
            messages.success(request, f'✅ Entrée de {quantite} unités de "{produit.nom}" enregistrée !')
            return redirect('stock:dashboard')
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    produits = Produit.objects.all().order_by('nom')
    return render(request, 'stock/entree.html', {'produits': produits})


# ===========================
# 📤 VENTES / SORTIES (Admin + Vendeurs)
# ===========================

@login_required
def faire_vente(request):
    """Enregistrer une vente/sortie de stock"""
    if request.method == 'POST':
        try:
            produit_id = request.POST.get('produit')
            quantite = int(request.POST.get('quantite'))
            produit = get_object_or_404(Produit, id=produit_id)
            
            # Vérifier le stock
            if produit.stock_actuel < quantite:
                messages.error(request, f'❌ Stock insuffisant ! Disponible: {produit.stock_actuel}')
                return redirect('stock:vente')
            
            # Mise à jour du stock
            produit.stock_actuel -= quantite
            produit.save()
            
            # Créer le mouvement
            mouvement = Mouvement.objects.create(
                produit=produit,
                type_mouvement='VENTE',
                quantite=quantite,
                montant_total=quantite * produit.prix_unitaire,
                opere_par=request.user,
                commentaire=request.POST.get('commentaire', '')
            )
            
            # Log d'audit
            AuditLog.objects.create(
                action=f"VENTE: -{quantite} {produit.nom}",
                user=request.user
            )
            
            messages.success(request, f'✅ Vente de {quantite} unités enregistrée !')
            return redirect('stock:imprimer_vente', id=mouvement.id)
        except Exception as e:
            messages.error(request, f'❌ Erreur : {str(e)}')
    
    produits = Produit.objects.all().order_by('nom')
    produit_selectionne = None
    if request.GET.get('produit'):
        produit_selectionne = get_object_or_404(Produit, id=request.GET.get('produit'))
    
    return render(request, 'stock/vente.html', {
        'produits': produits,
        'produit_selectionne': produit_selectionne
    })

@login_required
def imprimer_vente(request, id):
    """Imprimer un reçu de vente"""
    mouvement = get_object_or_404(Mouvement, id=id)
    return render(request, 'stock/imprimer_vente.html', {'mouvement': mouvement})


# ===========================
# 🕐 HISTORIQUE & TRAÇABILITÉ
# ===========================

@login_required
def historique(request):
    """Historique de toutes les opérations"""
    mouvements = Mouvement.objects.all().select_related('produit', 'opere_par').order_by('-date_operation')
    
    # Filtres optionnels
    type_filter = request.GET.get('type')
    if type_filter:
        mouvements = mouvements.filter(type_mouvement=type_filter)
    
    date_debut = request.GET.get('date_debut')
    if date_debut:
        mouvements = mouvements.filter(date_operation__date__gte=date_debut)
    
    date_fin = request.GET.get('date_fin')
    if date_fin:
        mouvements = mouvements.filter(date_operation__date__lte=date_fin)
    
    return render(request, 'stock/historique.html', {'mouvements': mouvements})

@login_required
def imprimer_historique(request):
    """Imprimer l'historique"""
    mouvements = Mouvement.objects.all().select_related('produit', 'opere_par').order_by('-date_operation')
    return render(request, 'stock/imprimer_historique.html', {'mouvements': mouvements})


# ===========================
# 📊 RAPPORTS
# ===========================

@login_required
def rapport_stock_critique(request):
    """Rapport des produits en stock critique"""
    if not is_admin(request.user):
        messages.error(request, '⛔ Accès réservé aux administrateurs.')
        return redirect('stock:dashboard')
    
    # Récupération des produits critiques
    produits = Produit.objects.filter(stock_actuel__lte=F('seuil_critique')).order_by('stock_actuel')
    
    # Calcul des attributs supplémentaires pour l'affichage
    for produit in produits:
        # Valeur totale du stock en MRU (quantité × prix unitaire)
        # On utilise (produit.prix_unitaire or 0) pour éviter une erreur si le prix est None
        produit.valeur_stock = produit.stock_actuel * (produit.prix_unitaire or 0)
        # Écart par rapport au seuil (combien d'unités manquent pour atteindre le seuil)
        produit.ecart = produit.seuil_critique - produit.stock_actuel
    
    return render(request, 'stock/rapport_critique.html', {'produits': produits})

@login_required
def rapport_ventes(request):
    """Rapport des ventes"""
    if not is_admin(request.user):
        messages.error(request, '⛔ Accès réservé aux administrateurs.')
        return redirect('stock:dashboard')
    
    ventes = Mouvement.objects.filter(type_mouvement='VENTE').select_related('produit', 'opere_par').order_by('-date_operation')
    total_ventes = ventes.aggregate(total=Sum('montant_total'))['total'] or 0
    total_quantite = ventes.aggregate(total=Sum('quantite'))['total'] or 0
    
    return render(request, 'stock/rapport_ventes.html', {
        'ventes': ventes,
        'total_ventes': total_ventes,
        'total_quantite': total_quantite
    })

@login_required
def rapport_entrees(request):
    """Rapport des entrées"""
    if not is_admin(request.user):
        messages.error(request, '⛔ Accès réservé aux administrateurs.')
        return redirect('stock:dashboard')
    
    entrees = Mouvement.objects.filter(type_mouvement='ENTREE').select_related('produit', 'opere_par').order_by('-date_operation')
    total_entrees = entrees.aggregate(total=Sum('montant_total'))['total'] or 0
    total_quantite = entrees.aggregate(total=Sum('quantite'))['total'] or 0
    
    return render(request, 'stock/rapport_entrees.html', {
        'entrees': entrees,
        'total_entrees': total_entrees,
        'total_quantite': total_quantite
    })


# ===========================
# 🌐 API (Optionnel - pour AJAX)
# ===========================

@login_required
def api_stock_produit(request, produit_id):
    """API pour récupérer le stock d'un produit (AJAX)"""
    try:
        produit = Produit.objects.get(id=produit_id)
        return JsonResponse({
            'id': produit.id,
            'nom': produit.nom,
            'stock_actuel': produit.stock_actuel,
            'seuil_critique': produit.seuil_critique,
            'est_critique': produit.stock_actuel <= produit.seuil_critique,  # calcul direct
            'prix_unitaire': str(produit.prix_unitaire),
        })
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit non trouvé'}, status=404)