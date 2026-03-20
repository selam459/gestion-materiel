from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



class Produit(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="P.U (MRU)")
    stock_actuel = models.IntegerField(default=0, verbose_name="Quantité Existant")
    seuil_critique = models.IntegerField(default=5, verbose_name="Stock Critique")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.stock_actuel} u)"

    @property
    def est_critique(self):
        return self.stock_actuel <= self.seuil_critique

class Mouvement(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée Stock'),
        ('VENTE', 'Vente / Sortie'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant (MRU)")
    opere_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_operation = models.DateTimeField(default=timezone.now)
    commentaire = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        # Calcul automatique du montant
        self.montant_total = self.quantite * self.produit.prix_unitaire
        
        # Mise à jour du stock en temps réel
        if self.type_mouvement == 'ENTREE':
            self.produit.stock_actuel += self.quantite
        else:
            self.produit.stock_actuel -= self.quantite
            
        super().save(*args, **kwargs)
        self.produit.save() # Sauvegarde la mise à jour du stock

    def __str__(self):
        return f"{self.type_mouvement} - {self.produit.nom} - {self.quantite}"

class AuditLog(models.Model):
    # Pour la traçabilité avancée
    action = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)