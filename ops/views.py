from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Service, TypeFlux, MicroEvenement, Alerte, Rapport
from .serializers import (
    ServiceSerializer, TypeFluxSerializer, MicroEvenementSerializer, 
    AlerteSerializer, RapportSerializer
)
from hospyFlow_core.analytics_service import moteur_analyse
from hospyFlow_core.report_service import ReportGenerator, PDFExportStrategy, CSVExportStrategy

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    from rest_framework.decorators import action
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Returns a summary of all services with their current state and event counts.
        """
        from django.db.models import Count
        services = Service.objects.all()
        data = []
        for s in services:
            # Simple saturation calculation for the demo
            # In a real app, this would be based on active events vs capacity
            event_count = s.events.count()
            saturation = min(event_count * 10, 100) # Mock logic
            
            data.append({
                'id': s.id,
                'nom': s.nom,
                'etat': s.etat,
                'saturation': saturation,
                'event_count': event_count
            })
        
        # Add global KPIs
        kpis = {
            'waiting_avg': '24m',
            'flux_hour': sum(d['event_count'] for d in data),
            'risk_score': '5.8' if any(d['etat'] == 'TENSION' for d in data) else '2.1'
        }
        
        return Response({
            'services': data,
            'kpis': kpis
        })

class TypeFluxViewSet(viewsets.ModelViewSet):
    queryset = TypeFlux.objects.all()
    serializer_class = TypeFluxSerializer

class MicroEvenementViewSet(viewsets.ModelViewSet):
    queryset = MicroEvenement.objects.all()
    serializer_class = MicroEvenementSerializer

    def perform_create(self, serializer):
        # Save the event first
        instance = serializer.save()
        
        # Trigger the Singleton Analysis Engine
        # We pass the full object or enough data for the engine to decide
        nouvel_etat = moteur_analyse.analyser_evenement(instance)
        
        # Update service state if needed (State Pattern foundation)
        # Note: AdminNotifier (Observer) also handles this, but here we can 
        # explicitly ensure the service reflects the analysis result immediately
        if nouvel_etat == "TENSION" and instance.service.etat != "TENSION":
            instance.service.etat = "TENSION"
            instance.service.save()
            print(f"[API] Service {instance.service.nom} switched to TENSION via API")
        elif nouvel_etat == "NORMAL" and instance.service.etat == "TENSION":
            # Optional: logic to return to normal if analysis says so
            # For now, we manually reset or depend on another trigger
            pass

class AlerteViewSet(viewsets.ModelViewSet):
    queryset = Alerte.objects.all()
    serializer_class = AlerteSerializer

class RapportViewSet(viewsets.ModelViewSet):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer

    def perform_create(self, serializer):
        # Save instance first
        instance = serializer.save()
        
        # Determine format (could be passed in request data, default to pdf)
        export_format = self.request.data.get('format', 'pdf').lower()
        
        if export_format == 'csv':
            strategy = CSVExportStrategy()
        else:
            strategy = PDFExportStrategy()
            
        generator = ReportGenerator(strategy)
        filepath = generator.generate(instance, format=export_format)
        
        # Store relative path for frontend access
        relative_path = os.path.relpath(filepath, settings.BASE_DIR).replace('\\', '/')
        # Note: Ideally we'd have a FileField, but for the POC we can just 
        # return it in the response or mock it.
        print(f"[API] Report generated: {filepath}")
