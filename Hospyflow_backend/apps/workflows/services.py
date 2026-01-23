"""
Service Pattern - Couche de logique métier pour les workflows.
Contient toute la logique business et les règles métier.
"""
from typing import Optional, Dict, Any, List
from django.utils import timezone
from django.db import transaction

from .models import TypeWorkflow, EtapeWorkflow, InstanceWorkflow, TransitionEtape
from .repositories import (
    TypeWorkflowRepository,
    EtapeWorkflowRepository,
    InstanceWorkflowRepository,
    TransitionEtapeRepository
)


class WorkflowException(Exception):
    """Exception personnalisée pour les erreurs de workflow."""
    pass


class GestionWorkflowService:
    """
    Service principal pour la gestion des workflows.
    Implémente le pattern Facade pour orchestrer les opérations.
    """
    
    def __init__(self):
        self.type_repo = TypeWorkflowRepository()
        self.etape_repo = EtapeWorkflowRepository()
        self.instance_repo = InstanceWorkflowRepository()
        self.transition_repo = TransitionEtapeRepository()
    
    @transaction.atomic
    def demarrer_workflow(
        self,
        type_workflow_id: int,
        reference_patient: str,
        departement_id: int,
        utilisateur,
        priorite: str = 'NORMALE',
        notes: str = ''
    ) -> InstanceWorkflow:
        """
        Démarre une nouvelle instance de workflow.
        
        Args:
            type_workflow_id: ID du type de workflow
            reference_patient: Référence anonymisée du patient
            departement_id: ID du département
            utilisateur: Utilisateur qui initie le workflow
            priorite: Niveau de priorité
            notes: Notes additionnelles
        
        Returns:
            InstanceWorkflow: L'instance créée
        
        Raises:
            WorkflowException: Si le type de workflow n'existe pas
        """
        # Vérifier que le type de workflow existe
        type_workflow = self.type_repo.obtenir_par_id(type_workflow_id)
        if not type_workflow:
            raise WorkflowException("Type de workflow introuvable ou inactif.")
        
        # Obtenir la première étape
        premiere_etape = self.etape_repo.obtenir_premiere_etape(type_workflow_id)
        
        # Créer l'instance
        instance = self.instance_repo.creer({
            'type_workflow': type_workflow,
            'reference_patient': reference_patient,
            'etape_actuelle': premiere_etape,
            'statut': InstanceWorkflow.Statut.EN_COURS,
            'priorite': priorite,
            'departement_id': departement_id,
            'initie_par': utilisateur,
            'notes': notes
        })
        
        # Enregistrer la transition initiale
        if premiere_etape:
            self.transition_repo.creer({
                'instance': instance,
                'etape_source': None,
                'etape_destination': premiere_etape,
                'effectuee_par': utilisateur,
                'commentaire': 'Démarrage du workflow'
            })
        
        return instance
    
    @transaction.atomic
    def avancer_etape(
        self,
        instance_id: int,
        utilisateur,
        commentaire: str = ''
    ) -> InstanceWorkflow:
        """
        Fait avancer le workflow à l'étape suivante.
        
        Args:
            instance_id: ID de l'instance
            utilisateur: Utilisateur effectuant la transition
            commentaire: Commentaire optionnel
        
        Returns:
            InstanceWorkflow: L'instance mise à jour
        
        Raises:
            WorkflowException: Si l'instance n'existe pas ou ne peut pas avancer
        """
        instance = self.instance_repo.obtenir_par_id(instance_id)
        if not instance:
            raise WorkflowException("Instance de workflow introuvable.")
        
        if instance.statut in [InstanceWorkflow.Statut.TERMINE, InstanceWorkflow.Statut.ABANDONNE]:
            raise WorkflowException("Ce workflow est déjà terminé ou abandonné.")
        
        etape_actuelle = instance.etape_actuelle
        etape_suivante = None
        
        if etape_actuelle:
            etape_suivante = self.etape_repo.obtenir_etape_suivante(etape_actuelle)
        
        # Calculer la durée de l'étape actuelle
        duree_etape = None
        if etape_actuelle:
            derniere_transition = instance.transitions.order_by('-horodatage').first()
            if derniere_transition:
                duree_etape = int(
                    (timezone.now() - derniere_transition.horodatage).total_seconds() / 60
                )
        
        # Enregistrer la transition
        self.transition_repo.creer({
            'instance': instance,
            'etape_source': etape_actuelle,
            'etape_destination': etape_suivante,
            'effectuee_par': utilisateur,
            'duree_etape_minutes': duree_etape,
            'commentaire': commentaire
        })
        
        # Mettre à jour l'instance
        if etape_suivante:
            instance.etape_actuelle = etape_suivante
        else:
            # Fin du workflow
            instance.statut = InstanceWorkflow.Statut.TERMINE
            instance.termine_le = timezone.now()
            instance.etape_actuelle = None
        
        instance.save()
        return instance
    
    @transaction.atomic
    def abandonner_workflow(
        self,
        instance_id: int,
        utilisateur,
        raison: str = ''
    ) -> InstanceWorkflow:
        """
        Abandonne un workflow en cours.
        
        Args:
            instance_id: ID de l'instance
            utilisateur: Utilisateur effectuant l'abandon
            raison: Raison de l'abandon
        
        Returns:
            InstanceWorkflow: L'instance mise à jour
        """
        instance = self.instance_repo.obtenir_par_id(instance_id)
        if not instance:
            raise WorkflowException("Instance de workflow introuvable.")
        
        # Enregistrer la transition d'abandon
        self.transition_repo.creer({
            'instance': instance,
            'etape_source': instance.etape_actuelle,
            'etape_destination': None,
            'effectuee_par': utilisateur,
            'commentaire': f"Workflow abandonné: {raison}"
        })
        
        instance.statut = InstanceWorkflow.Statut.ABANDONNE
        instance.termine_le = timezone.now()
        instance.save()
        
        return instance
    
    def mettre_en_pause(self, instance_id: int) -> InstanceWorkflow:
        """Met un workflow en pause."""
        instance = self.instance_repo.obtenir_par_id(instance_id)
        if not instance:
            raise WorkflowException("Instance de workflow introuvable.")
        
        if instance.statut != InstanceWorkflow.Statut.EN_COURS:
            raise WorkflowException("Seul un workflow en cours peut être mis en pause.")
        
        instance.statut = InstanceWorkflow.Statut.EN_PAUSE
        instance.save()
        return instance
    
    def reprendre(self, instance_id: int) -> InstanceWorkflow:
        """Reprend un workflow en pause."""
        instance = self.instance_repo.obtenir_par_id(instance_id)
        if not instance:
            raise WorkflowException("Instance de workflow introuvable.")
        
        if instance.statut != InstanceWorkflow.Statut.EN_PAUSE:
            raise WorkflowException("Seul un workflow en pause peut être repris.")
        
        instance.statut = InstanceWorkflow.Statut.EN_COURS
        instance.save()
        return instance
    
    def obtenir_workflows_en_retard(self) -> List[InstanceWorkflow]:
        """Retourne tous les workflows qui ont dépassé leur seuil d'alerte."""
        instances_en_cours = self.instance_repo.obtenir_en_cours()
        en_retard = []
        
        for instance in instances_en_cours:
            if instance.est_en_retard:
                en_retard.append(instance)
        
        return en_retard
    
    def obtenir_progression_workflow(self, instance_id: int) -> Dict[str, Any]:
        """
        Calcule la progression d'un workflow.
        
        Returns:
            Dict contenant les informations de progression
        """
        instance = self.instance_repo.obtenir_par_id(instance_id)
        if not instance:
            raise WorkflowException("Instance de workflow introuvable.")
        
        etapes = list(self.etape_repo.obtenir_etapes_workflow(
            instance.type_workflow_id
        ))
        
        etapes_completees = instance.transitions.filter(
            etape_destination__isnull=False
        ).values_list('etape_destination_id', flat=True)
        
        total_etapes = len(etapes)
        etapes_faites = len(set(etapes_completees))
        
        pourcentage = (etapes_faites / total_etapes * 100) if total_etapes > 0 else 0
        
        return {
            'instance_id': instance.id,
            'total_etapes': total_etapes,
            'etapes_completees': etapes_faites,
            'pourcentage_completion': round(pourcentage, 1),
            'etape_actuelle': instance.etape_actuelle.nom if instance.etape_actuelle else None,
            'duree_ecoulee_minutes': instance.duree_ecoulee_minutes,
            'est_en_retard': instance.est_en_retard,
            'statut': instance.statut
        }
