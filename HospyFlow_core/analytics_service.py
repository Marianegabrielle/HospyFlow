from .alert_service import Subject, AdminNotifier

class MoteurAnalyse(Subject):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MoteurAnalyse, cls).__new__(cls)
            # Initialize Subject part
            super(MoteurAnalyse, cls._instance).__init__()
            # Attach default observers
            cls._instance.attach(AdminNotifier())
        return cls._instance

    def analyser_evenement(self, evenement):
        """
        Analyses a MicroEvenement instance to detect bottlenecks.
        """
        print(f"[ANALYSE] Processing event: {evenement.type_flux.nom} for {evenement.service.nom}")
        
        is_bottleneck = False
        
        # Logic 1: Immediate bottleneck if severity is CRITICAL
        if evenement.niveau_gravite == 'CRITICAL':
            is_bottleneck = True
            reason = f"Critical event detected: {evenement.description}"
        
        # Logic 2: Detection by frequency (could be added here)
        # For now, let's stick to gravity for the POC
            
        if is_bottleneck:
            alert_data = {
                'message': reason,
                'service_id': evenement.service.id,
                'type': 'BOTTLENECK'
            }
            self.notify(alert_data)
            return "TENSION"
            
        return "NORMAL"

# Global access point (Singleton)
moteur_analyse = MoteurAnalyse()
