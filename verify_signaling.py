import os
import django
import sys

# Set up Django environment
sys.path.append('c:/Documents/HospyFlow')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospyFlow_core.settings')
django.setup()

from ops.models import Service, TypeFlux, MicroEvenement
from django.contrib.auth.models import User
from hospyFlow_core.analytics_service import moteur_analyse

def test_signaling_flow():
    print("--- Testing Hospital Signaling Flow ---")
    
    # 1. Setup sample data
    user, _ = User.objects.get_or_create(username="test_admin")
    service, _ = Service.objects.get_or_create(nom="Urgences", defaults={'localisation': 'Aile A'})
    type_flux, _ = TypeFlux.objects.get_or_create(nom="Saturation", defaults={'duree_standard': 3600})
    
    # Ensure service is NORMAL initially
    service.etat = 'NORMAL'
    service.save()
    print(f"Initial State for {service.nom}: {service.etat}")
    
    # 2. Simulate a CRITICAL event
    print("\nSimulating a CRITICAL saturation event...")
    event = MicroEvenement.objects.create(
        personnel=user,
        service=service,
        type_flux=type_flux,
        description="Saturation critique détectée",
        niveau_gravite='CRITICAL'
    )
    
    # 3. Manually call the analysis if we want to test the analytical logic directly
    # But perform_create in views.py already does this. 
    # Since we are using models.create here, it doesn't trigger view logic.
    # Let's call the engine directly as views.py would.
    nouvel_etat = moteur_analyse.analyser_evenement(event)
    print(f"Analysis Result: {nouvel_etat}")
    
    # In views.py, we update the state:
    if nouvel_etat == "TENSION":
        service.etat = "TENSION"
        service.save()
    
    # 4. Verify results
    updated_service = Service.objects.get(id=service.id)
    print(f"Final State for {service.nom}: {updated_service.etat}")
    
    if updated_service.etat == 'TENSION':
        print("\nSUCCESS: Flow verified. Micro-event triggered TENSION state.")
    else:
        print("\nFAILURE: Service state did not change.")

if __name__ == "__main__":
    test_signaling_flow()
