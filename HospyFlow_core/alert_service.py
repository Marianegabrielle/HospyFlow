from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, alert_data):
        pass

class Subject(ABC):
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, alert_data):
        print(f"[DEBUG] Notifying {len(self._observers)} observers with: {alert_data['message']}")
        for observer in self._observers:
            observer.update(alert_data)

class AdminNotifier(Observer):
    def update(self, alert_data):
        from ops.models import Alerte, Service
        
        # 1. Create the alert in the database
        service_id = alert_data.get('service_id')
        try:
            service = Service.objects.get(id=service_id)
            Alerte.objects.create(
                service=service,
                message=alert_data['message'],
                niveau_gravite=alert_data.get('type', 'HIGH') # Map type to gravity or use a default
            )
            
            # 2. Update service state to TENSION (State Pattern)
            if service.etat != 'TENSION':
                service.etat = 'TENSION'
                service.save()
                print(f"[STATE] Service {service.nom} switched to TENSION")

            print(f"[NOTIF] Alert persisted: {alert_data['message']} for {service.nom}")
            
        except Service.DoesNotExist:
            print(f"[ERROR] Service ID {service_id} not found for alert")
