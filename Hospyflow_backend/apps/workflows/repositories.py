"""
Repository Pattern - Couche d'accès aux données pour les workflows.
Centralise toutes les requêtes à la base de données.
"""
from typing import List, Optional
from django.db.models import QuerySet, Count, Avg, F
from django.utils import timezone
from datetime import timedelta

from .models import TypeWorkflow, EtapeWorkflow, InstanceWorkflow, TransitionEtape


class TypeWorkflowRepository:
    """Repository pour les types de workflows."""
    
    @staticmethod
    def obtenir_tous_actifs() -> QuerySet[TypeWorkflow]:
        """Retourne tous les types de workflows actifs."""
        return TypeWorkflow.objects.filter(est_actif=True).order_by('ordre_affichage')
    
    @staticmethod
    def obtenir_par_id(workflow_id: int) -> Optional[TypeWorkflow]:
        """Retourne un type de workflow par son ID."""
        try:
            return TypeWorkflow.objects.get(pk=workflow_id, est_actif=True)
        except TypeWorkflow.DoesNotExist:
            return None
    
    @staticmethod
    def obtenir_par_code(code: str) -> Optional[TypeWorkflow]:
        """Retourne un type de workflow par son code."""
        try:
            return TypeWorkflow.objects.get(code=code, est_actif=True)
        except TypeWorkflow.DoesNotExist:
            return None
    
    @staticmethod
    def obtenir_par_categorie(categorie: str) -> QuerySet[TypeWorkflow]:
        """Retourne les types de workflows par catégorie."""
        return TypeWorkflow.objects.filter(
            categorie=categorie,
            est_actif=True
        ).order_by('ordre_affichage')
    
    @staticmethod
    def obtenir_avec_statistiques() -> QuerySet:
        """Retourne les types avec le nombre d'instances."""
        return TypeWorkflow.objects.filter(est_actif=True).annotate(
            nombre_instances=Count('instances'),
            instances_en_cours=Count(
                'instances',
                filter=models.Q(instances__statut='EN_COURS')
            )
        )


class EtapeWorkflowRepository:
    """Repository pour les étapes de workflows."""
    
    @staticmethod
    def obtenir_etapes_workflow(type_workflow_id: int) -> QuerySet[EtapeWorkflow]:
        """Retourne les étapes ordonnées d'un type de workflow."""
        return EtapeWorkflow.objects.filter(
            type_workflow_id=type_workflow_id
        ).order_by('ordre')
    
    @staticmethod
    def obtenir_premiere_etape(type_workflow_id: int) -> Optional[EtapeWorkflow]:
        """Retourne la première étape d'un workflow."""
        return EtapeWorkflow.objects.filter(
            type_workflow_id=type_workflow_id
        ).order_by('ordre').first()
    
    @staticmethod
    def obtenir_etape_suivante(etape_actuelle: EtapeWorkflow) -> Optional[EtapeWorkflow]:
        """Retourne l'étape suivante dans le workflow."""
        return EtapeWorkflow.objects.filter(
            type_workflow=etape_actuelle.type_workflow,
            ordre__gt=etape_actuelle.ordre
        ).order_by('ordre').first()


class InstanceWorkflowRepository:
    """Repository pour les instances de workflows."""
    
    @staticmethod
    def creer(donnees: dict) -> InstanceWorkflow:
        """Crée une nouvelle instance de workflow."""
        return InstanceWorkflow.objects.create(**donnees)
    
    @staticmethod
    def obtenir_par_id(instance_id: int) -> Optional[InstanceWorkflow]:
        """Retourne une instance par son ID."""
        try:
            return InstanceWorkflow.objects.select_related(
                'type_workflow', 'etape_actuelle', 'departement', 'initie_par'
            ).get(pk=instance_id)
        except InstanceWorkflow.DoesNotExist:
            return None
    
    @staticmethod
    def obtenir_en_cours() -> QuerySet[InstanceWorkflow]:
        """Retourne toutes les instances en cours."""
        return InstanceWorkflow.objects.filter(
            statut__in=['INITIE', 'EN_COURS', 'EN_PAUSE']
        ).select_related('type_workflow', 'etape_actuelle', 'departement')
    
    @staticmethod
    def obtenir_par_departement(departement_id: int) -> QuerySet[InstanceWorkflow]:
        """Retourne les instances d'un département."""
        return InstanceWorkflow.objects.filter(
            departement_id=departement_id
        ).select_related('type_workflow', 'etape_actuelle')
    
    @staticmethod
    def obtenir_en_retard() -> QuerySet[InstanceWorkflow]:
        """Retourne les instances qui dépassent le seuil d'alerte."""
        maintenant = timezone.now()
        return InstanceWorkflow.objects.filter(
            statut__in=['INITIE', 'EN_COURS']
        ).annotate(
            duree_minutes=(maintenant - F('demarre_le'))
        ).filter(
            duree_minutes__gt=F('type_workflow__seuil_alerte_minutes') * 60
        )
    
    @staticmethod
    def obtenir_statistiques_periode(debut: timezone, fin: timezone) -> dict:
        """Retourne les statistiques sur une période."""
        instances = InstanceWorkflow.objects.filter(
            demarre_le__gte=debut,
            demarre_le__lte=fin
        )
        return {
            'total': instances.count(),
            'terminees': instances.filter(statut='TERMINE').count(),
            'en_cours': instances.filter(statut='EN_COURS').count(),
            'abandonnees': instances.filter(statut='ABANDONNE').count(),
        }


class TransitionEtapeRepository:
    """Repository pour les transitions d'étapes."""
    
    @staticmethod
    def creer(donnees: dict) -> TransitionEtape:
        """Crée une nouvelle transition."""
        return TransitionEtape.objects.create(**donnees)
    
    @staticmethod
    def obtenir_historique_instance(instance_id: int) -> QuerySet[TransitionEtape]:
        """Retourne l'historique des transitions d'une instance."""
        return TransitionEtape.objects.filter(
            instance_id=instance_id
        ).select_related('etape_source', 'etape_destination', 'effectuee_par')
    
    @staticmethod
    def calculer_duree_moyenne_etape(etape_id: int) -> Optional[float]:
        """Calcule la durée moyenne d'une étape."""
        result = TransitionEtape.objects.filter(
            etape_source_id=etape_id,
            duree_etape_minutes__isnull=False
        ).aggregate(moyenne=Avg('duree_etape_minutes'))
        return result['moyenne']
