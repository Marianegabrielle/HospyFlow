from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Department
from apps.services.models import ServiceHospitalier
from apps.events.models import MicroEvenement, CategorieEvenement
from apps.alerts.models import Alerte
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed initial data for HospyFlow'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # 1. Create Departments
        departments_data = [
            {'name': 'Urgences', 'code': 'URG', 'building': 'Batiment A', 'floor': '0'},
            {'name': 'Cardiologie', 'code': 'CAR', 'building': 'Batiment B', 'floor': '1'},
            {'name': 'Chirurgie', 'code': 'CHI', 'building': 'Batiment A', 'floor': '2'},
            {'name': 'Pédiatrie', 'code': 'PED', 'building': 'Batiment C', 'floor': '1'},
            {'name': 'Radiologie', 'code': 'RAD', 'building': 'Batiment B', 'floor': '0'},
        ]
        
        departments = {}
        for data in departments_data:
            dept, created = Department.objects.get_or_create(
                name=data['name'],
                defaults={
                    'code': data['code'],
                    'building': data['building'], 
                    'floor': data['floor']
                }
            )
            # If exists but code is empty or different (should not happen with name check but to be safe)
            if not created and not dept.code:
                dept.code = data['code']
                dept.save()
            departments[data['name']] = dept
            if created:
                self.stdout.write(f'Created Department: {dept.name}')

        # 2. Create ServiceHospitalier (Extensions of Department)
        for name, dept in departments.items():
            service, created = ServiceHospitalier.objects.get_or_create(
                department=dept,
                defaults={'saturation': random.randint(10, 90)}
            )
            service.calculer_saturation()
            if created:
                self.stdout.write(f'Created ServiceHospitalier: {service.nom}')

        # 3. Create Users
        users_data = [
            {'first_name': 'Admin', 'last_name': 'System', 'email': 'admin@hospyflow.com', 'role': 'ADMIN', 'password': 'password123'},
            {'first_name': 'Doctor', 'last_name': 'Urgences', 'email': 'doc@hospyflow.com', 'role': 'DOCTOR', 'department': departments['Urgences'], 'password': 'password123'},
            {'first_name': 'Doctor', 'last_name': 'Cardio', 'email': 'cardio@hospyflow.com', 'role': 'DOCTOR', 'department': departments['Cardiologie'], 'password': 'password123'},
            {'first_name': 'Nurse', 'last_name': 'One', 'email': 'nurse@hospyflow.com', 'role': 'NURSE', 'department': departments['Urgences'], 'password': 'password123'},
        ]

        for u_data in users_data:
            if not User.objects.filter(email=u_data['email']).exists():
                user = User.objects.create_user(
                    email=u_data['email'],
                    password=u_data['password'],
                    first_name=u_data['first_name'],
                    last_name=u_data['last_name'],
                    role=u_data['role'],
                    department=u_data.get('department')
                )
                if u_data['role'] == 'ADMIN':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                self.stdout.write(f'Created User: {user.email}')

        # 4. Create Event Categories
        categories = [
            {'nom': 'Matériel', 'code': 'MAT'},
            {'nom': 'Personnel', 'code': 'PERS'},
            {'nom': 'Patient', 'code': 'PAT'},
            {'nom': 'Logistique', 'code': 'LOG'},
        ]
        cat_objs = []
        for cat_data in categories:
            obj, _ = CategorieEvenement.objects.get_or_create(
                nom=cat_data['nom'],
                defaults={'code': cat_data['code']}
            )
            if not obj.code:
                obj.code = cat_data['code']
                obj.save()
            cat_objs.append(obj)

        # 5. Create MicroEvents
        statuses = ['SIGNALE', 'EN_COURS', 'RESOLU']
        severities = ['BASSE', 'MOYENNE', 'HAUTE', 'CRITIQUE']
        
        if MicroEvenement.objects.count() < 10:
            for _ in range(15):
                dept = random.choice(list(departments.values()))
                MicroEvenement.objects.create(
                    titre=random.choice(['Panne Moniteur', 'Manque Brancard', 'Patient Agité', 'Stock épuisé']),
                    description="Événement généré automatiquement",
                    categorie=random.choice(cat_objs),
                    severite=random.choice(severities),
                    statut=random.choice(statuses),
                    departement=dept,
                    rapporteur=User.objects.filter(role__in=['DOCTOR', 'NURSE']).first()
                )
            self.stdout.write('Created random MicroEvents')
            
        # Update saturations
        for s in ServiceHospitalier.objects.all():
            s.calculer_saturation()

        self.stdout.write(self.style.SUCCESS('Successfully seeded initial data'))
