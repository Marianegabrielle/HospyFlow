"""
Serializers pour l'API Services.
"""
from rest_framework import serializers
from .models import ServiceHospitalier
from apps.accounts.models import Department


class ServiceHospitalierSerializer(serializers.ModelSerializer):
    """Serializer pour ServiceHospitalier avec compatibilité ancien backend."""
    
    id = serializers.IntegerField(source='department.id', read_only=True)
    nom = serializers.CharField(source='department.name', read_only=True)
    code = serializers.CharField(source='department.code', read_only=True)
    description = serializers.CharField(source='department.description', read_only=True)
    capacite = serializers.IntegerField(default=20, read_only=True)
    responsable = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceHospitalier
        fields = ['id', 'nom', 'code', 'localisation', 'description', 'capacite', 'responsable', 'etat', 'saturation', 'derniere_maj']
        read_only_fields = ['saturation', 'derniere_maj']
    
    def get_localisation(self, obj):
        """Retourne la localisation formatée."""
        dept = obj.department
        if dept.building and dept.floor:
            return f"{dept.building} - {dept.floor}"
        return dept.building or dept.floor or ""

    def get_responsable(self, obj):
        """Retourne le nom du responsable (premier médecin ou admin)."""
        # Logique simplifiée pour l'exemple
        from apps.accounts.models import User
        # Chercher un médecin du département
        doctor = obj.department.staff.filter(role='DOCTOR').first()
        if doctor:
            return f"Dr. {doctor.last_name}"
        return "Dr. Responsable"


class ServiceSummarySerializer(serializers.Serializer):
    """
    Serializer pour le résumé des services.
    Compatible avec l'ancien endpoint /api/services/summary/
    """
    services = serializers.SerializerMethodField()
    kpis = serializers.SerializerMethodField()
    
    def get_services(self, obj):
        """Retourne la liste des services avec leurs métriques."""
        from apps.events.models import MicroEvenement
        from django.utils import timezone
        from datetime import timedelta
        
        services_data = []
        services = ServiceHospitalier.objects.select_related('department').all()
        
        for service in services:
            # Recalculer la saturation
            service.calculer_saturation()
            
            # Compter les événements récents
            depuis = timezone.now() - timedelta(hours=24)
            event_count = MicroEvenement.objects.filter(
                departement=service.department,
                signale_le__gte=depuis
            ).count()
            
            services_data.append({
                'id': service.department.id,
                'nom': service.department.name,
                'etat': service.etat,
                'saturation': service.saturation,
                'event_count': event_count
            })
        
        return services_data
    
    def get_kpis(self, obj):
        """Retourne les KPIs globaux."""
        from apps.events.models import MicroEvenement
        from apps.workflows.models import InstanceWorkflow
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg
        
        depuis = timezone.now() - timedelta(hours=24)
        
        # Temps d'attente moyen (basé sur les workflows)
        workflows_termines = InstanceWorkflow.objects.filter(
            termine_le__gte=depuis,
            statut='TERMINE'
        )
        
        duree_moyenne = 0
        if workflows_termines.exists():
            durees = []
            for wf in workflows_termines:
                if wf.duree_ecoulee_minutes:
                    durees.append(wf.duree_ecoulee_minutes)
            
            if durees:
                duree_moyenne = sum(durees) / len(durees)
        
        # Formater en minutes
        waiting_avg = f"{int(duree_moyenne)}m" if duree_moyenne > 0 else "--"
        
        # Flux par heure (événements récents)
        flux_hour = MicroEvenement.objects.filter(
            signale_le__gte=depuis
        ).count()
        
        # Score de risque (basé sur événements critiques)
        evenements_critiques = MicroEvenement.objects.filter(
            signale_le__gte=depuis,
            severite='CRITIQUE'
        ).count()
        
        evenements_total = MicroEvenement.objects.filter(
            signale_le__gte=depuis
        ).count()
        
        if evenements_total > 0:
            risk_score = (evenements_critiques / evenements_total) * 10
        else:
            risk_score = 0
        
        # Vérifier si au moins un service est en tension
        services_tension = ServiceHospitalier.objects.filter(etat='TENSION').exists()
        if services_tension:
            risk_score = max(risk_score, 5.8)
        
        return {
            'waiting_avg': waiting_avg,
            'flux_hour': flux_hour,
            'risk_score': f"{risk_score:.1f}"
        }
