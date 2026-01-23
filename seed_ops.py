import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospyFlow_core.settings')
django.setup()

from django.contrib.auth.models import User
from ops.models import Service, TypeFlux

def seed():
    print("--- Seeding HospyFlow Data ---")
    
    # 1. Ensure superuser exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Created superuser: admin/admin")
    
    # 2. Seed Services
    services = [
        {'nom': 'Urgences', 'localisation': 'Aile A, RDC'},
        {'nom': 'Radiologie', 'localisation': 'Aile B, Etage 1'},
        {'nom': 'Bloc Opératoire', 'localisation': 'Aile C, Etage 2'},
        {'nom': 'Laboratoire', 'localisation': 'Aile A, Etage 1'},
    ]
    
    for s_data in services:
        obj, created = Service.objects.get_or_create(nom=s_data['nom'], defaults={'localisation': s_data['localisation']})
        if created:
            print(f"Created Service: {obj.nom}")
        else:
            print(f"Service exists: {obj.nom}")

    # 3. Seed TypeFlux
    flux_types = [
        {'nom': 'Admission Patient', 'duree_standard': 600}, # 10 min
        {'nom': 'Transfert Inter-service', 'duree_standard': 300}, # 5 min
        {'nom': 'Examen Labo', 'duree_standard': 1800}, # 30 min
        {'nom': 'Consultation Spécialisée', 'duree_standard': 900}, # 15 min
    ]
    
    for f_data in flux_types:
        obj, created = TypeFlux.objects.get_or_create(nom=f_data['nom'], defaults={'duree_standard': f_data['duree_standard']})
        if created:
            print(f"Created Flux Type: {obj.nom}")
        else:
            print(f"Flux Type exists: {obj.nom}")

    print("--- Seeding Complete ---")

if __name__ == "__main__":
    seed()
