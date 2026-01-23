import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospyFlow_core.settings')
django.setup()

from ops.models import Service, MicroEvenement, TypeFlux, Alerte, User

def verify():
    print("--- Verification of Analytics & Alerts ---")
    
    # 1. Setup
    service = Service.objects.first()
    flux = TypeFlux.objects.first()
    user = User.objects.get(username='admin')
    
    # Reset service state
    service.etat = 'NORMAL'
    service.save()
    Alerte.objects.all().delete()
    
    print(f"Testing with Service: {service.nom}")
    
    # 2. Normal Event
    print("\n[Step 1] Creating a NORMAL event...")
    MicroEvenement.objects.create(
        personnel=user,
        service=service,
        type_flux=flux,
        description="Tout va bien",
        niveau_gravite='LOW'
    )
    
    service.refresh_from_db()
    alerts_count = Alerte.objects.count()
    print(f"Service state: {service.etat} (Expected: NORMAL)")
    print(f"Alerts count: {alerts_count} (Expected: 0)")
    
    # 3. Critical Event
    print("\n[Step 2] Creating a CRITICAL event...")
    MicroEvenement.objects.create(
        personnel=user,
        service=service,
        type_flux=flux,
        description="Goulot d'étranglement majeur !",
        niveau_gravite='CRITICAL'
    )
    
    service.refresh_from_db()
    alerts = Alerte.objects.all()
    print(f"Service state: {service.etat} (Expected: TENSION)")
    print(f"Alerts count: {alerts.count()} (Expected: 1)")
    if alerts.exists():
        print(f"Alert Message: {alerts.first().message}")

    print("\n--- Verification Completed ---")

if __name__ == "__main__":
    verify()
