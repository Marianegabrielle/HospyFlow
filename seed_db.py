import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospyFlow_core.settings')
django.setup()

from ops.models import Service, TypeFlux

def seed():
    print("Seeding database...")
    
    # 1. Create Services
    services = [
        {'nom': 'Urgences', 'localisation': 'Aile A, Niveau 0'},
        {'nom': 'Radiologie', 'localisation': 'Aile B, Niveau 1'},
        {'nom': 'Pédiatrie', 'localisation': 'Aile C, Niveau 2'},
        {'nom': 'Bloc Opératoire', 'localisation': 'Aile D, Niveau 1'},
        {'nom': 'Laboratoire', 'localisation': 'Aile B, Niveau 0'},
    ]
    
    for s_data in services:
        obj, created = Service.objects.get_or_create(
            nom=s_data['nom'], 
            defaults={'localisation': s_data['localisation']}
        )
        if created:
            print(f"Created Service: {obj.nom}")

    # 2. Create TypeFlux
    flux_types = [
        {'nom': 'Retard Flux', 'duree_standard': 3600},
        {'nom': 'Panne Matériel', 'duree_standard': 7200},
        {'nom': 'Manque Personnel', 'duree_standard': 18000},
        {'nom': 'Saturation', 'duree_standard': 3600},
    ]
    
    for f_data in flux_types:
        obj, created = TypeFlux.objects.get_or_create(
            nom=f_data['nom'], 
            defaults={'duree_standard': f_data['duree_standard']}
        )
        if created:
            print(f"Created TypeFlux: {obj.nom}")

    # 3. Create a Superuser (optional but helpful for demo)
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@hospyflow.com', 'admin123')
        print("Created superuser 'admin' with password 'admin123'")

    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
