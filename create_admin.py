# create_admin.py - À SUPPRIMER APRÈS USAGE !
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_materiel.settings')  # ← Adaptez au nom de votre projet
django.setup()

from django.contrib.auth.models import User

username = 'admin'
email = 'selamsalem02@gmail.com'
password = 'Hmd2526@'  # ← Changez ce mot de passe !

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"✅ Superutilisateur '{username}' créé avec succès !")
else:
    print(f"⚠️ L'utilisateur '{username}' existe déjà.")