"""
Service Pattern - Gestion des alertes et notifications.
Implémente le pattern Observer pour les notifications.
"""
from typing import List, Optional, Dict, Any
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from .models import Alerte, RegleAlerte, AbonnementAlerte
from apps.events.models import MicroEvenement
from apps.analytics.models import AnalyseGoulotEtranglement
from apps.workflows.models import InstanceWorkflow


class AlerteException(Exception):
    """Exception pour les erreurs d'alertes."""
    pass


class GestionAlerteService:
    """
    Service principal pour la gestion des alertes.
    Implémente le pattern Observer pour les notifications.
    """
    
    @transaction.atomic
    def creer_alerte(
        self,
        titre: str,
        message: str,
        priorite: str = 'NORMALE',
        departement_id: Optional[int] = None,
        regle_id: Optional[int] = None,
        evenement_id: Optional[int] = None,
        goulot_id: Optional[int] = None,
        workflow_id: Optional[int] = None,
        donnees_contexte: Optional[Dict] = None
    ) -> Alerte:
        """
        Crée une nouvelle alerte.
        
        Args:
            titre: Titre de l'alerte
            message: Message détaillé
            priorite: Niveau de priorité
            departement_id: ID du département concerné
            regle_id: ID de la règle déclencheuse
            evenement_id: ID de l'événement lié
            goulot_id: ID du goulot lié
            workflow_id: ID du workflow lié
            donnees_contexte: Données additionnelles
        
        Returns:
            Alerte: L'alerte créée
        """
        alerte = Alerte.objects.create(
            titre=titre,
            message=message,
            priorite=priorite,
            departement_id=departement_id,
            regle_id=regle_id,
            evenement_id=evenement_id,
            goulot_id=goulot_id,
            workflow_id=workflow_id,
            donnees_contexte=donnees_contexte or {}
        )
        
        # Notifier les abonnés (pattern Observer)
        self._notifier_abonnes(alerte)
        
        return alerte
    
    def _notifier_abonnes(self, alerte: Alerte):
        """
        Notifie les abonnés concernés par l'alerte.
        Pattern Observer.
        """
        # Obtenir les abonnés éligibles
        abonnes = AbonnementAlerte.objects.filter(
            est_actif=True
        )
        
        # Filtrer par priorité
        priorites_ordre = ['BASSE', 'NORMALE', 'HAUTE', 'URGENTE']
        index_alerte = priorites_ordre.index(alerte.priorite)
        
        for abonne in abonnes:
            index_min = priorites_ordre.index(abonne.priorite_minimum)
            if index_alerte < index_min:
                continue
            
            # Vérifier le département
            if abonne.departements.exists():
                if alerte.departement_id and alerte.departement_id not in abonne.departements.values_list('id', flat=True):
                    continue
            
            # TODO: Implémenter l'envoi réel (push, email, SMS)
            self._envoyer_notification(abonne, alerte)
    
    def _envoyer_notification(self, abonnement: AbonnementAlerte, alerte: Alerte):
        """Envoie la notification selon le canal."""
        # TODO: Implémenter les différents canaux
        # Pour l'instant, on log juste
        pass
    
    def marquer_vue(self, alerte_id: int) -> Alerte:
        """Marque une alerte comme vue."""
        try:
            alerte = Alerte.objects.get(pk=alerte_id)
        except Alerte.DoesNotExist:
            raise AlerteException("Alerte introuvable.")
        
        if alerte.statut == 'NOUVELLE':
            alerte.statut = 'VUE'
            alerte.vue_le = timezone.now()
            alerte.save()
        
        return alerte
    
    def acquitter(self, alerte_id: int, utilisateur) -> Alerte:
        """Acquitte une alerte."""
        try:
            alerte = Alerte.objects.get(pk=alerte_id)
        except Alerte.DoesNotExist:
            raise AlerteException("Alerte introuvable.")
        
        alerte.statut = 'ACQUITTEE'
        alerte.acquittee_le = timezone.now()
        alerte.acquittee_par = utilisateur
        alerte.save()
        
        return alerte
    
    def resoudre(self, alerte_id: int) -> Alerte:
        """Résout une alerte."""
        try:
            alerte = Alerte.objects.get(pk=alerte_id)
        except Alerte.DoesNotExist:
            raise AlerteException("Alerte introuvable.")
        
        alerte.statut = 'RESOLUE'
        alerte.resolue_le = timezone.now()
        alerte.save()
        
        return alerte
    
    def ignorer(self, alerte_id: int) -> Alerte:
        """Ignore une alerte."""
        try:
            alerte = Alerte.objects.get(pk=alerte_id)
        except Alerte.DoesNotExist:
            raise AlerteException("Alerte introuvable.")
        
        alerte.statut = 'IGNOREE'
        alerte.save()
        
        return alerte
    
    def obtenir_alertes_utilisateur(
        self,
        utilisateur,
        non_lues_seulement: bool = False
    ) -> List[Alerte]:
        """
        Obtient les alertes pertinentes pour un utilisateur.
        
        Args:
            utilisateur: L'utilisateur
            non_lues_seulement: Si True, retourne seulement les nouvelles
        
        Returns:
            Liste des alertes
        """
        queryset = Alerte.objects.all()
        
        if non_lues_seulement:
            queryset = queryset.filter(statut='NOUVELLE')
        
        # Filtrer par département de l'utilisateur si applicable
        if utilisateur.department:
            queryset = queryset.filter(
                Q(departement=utilisateur.department) |
                Q(departement__isnull=True)
            )
        
        # Les admins voient tout
        if utilisateur.is_admin:
            queryset = Alerte.objects.filter(
                statut='NOUVELLE'
            ) if non_lues_seulement else Alerte.objects.all()
        
        return list(queryset.order_by('-cree_le')[:50])


class MoteurReglesService:
    """
    Service d'évaluation des règles d'alerte.
    Vérifie périodiquement les conditions et génère des alertes.
    """
    
    def __init__(self):
        self.alerte_service = GestionAlerteService()
    
    def evaluer_toutes_regles(self):
        """
        Évalue toutes les règles actives.
        À exécuter périodiquement via tâche planifiée.
        """
        regles = RegleAlerte.objects.filter(est_actif=True)
        alertes_generees = []
        
        for regle in regles:
            alertes = self._evaluer_regle(regle)
            alertes_generees.extend(alertes)
        
        return alertes_generees
    
    def _evaluer_regle(self, regle: RegleAlerte) -> List[Alerte]:
        """Évalue une règle spécifique."""
        evaluateurs = {
            'SEUIL_EVENEMENTS': self._evaluer_seuil_evenements,
            'SEUIL_TEMPS': self._evaluer_seuil_temps,
            'EVENEMENT_CRITIQUE': self._evaluer_evenement_critique,
            'GOULOT_DETECTE': self._evaluer_goulot_detecte,
            'WORKFLOW_RETARD': self._evaluer_workflow_retard
        }
        
        evaluateur = evaluateurs.get(regle.type_regle)
        if evaluateur:
            return evaluateur(regle)
        
        return []
    
    def _evaluer_seuil_evenements(self, regle: RegleAlerte) -> List[Alerte]:
        """Évalue le seuil d'événements."""
        from datetime import timedelta
        
        depuis = timezone.now() - timedelta(minutes=regle.periode_minutes)
        
        queryset = MicroEvenement.objects.filter(
            signale_le__gte=depuis,
            statut__in=['SIGNALE', 'EN_COURS']
        )
        
        if regle.departement:
            queryset = queryset.filter(departement=regle.departement)
        
        nombre = queryset.count()
        
        if nombre >= regle.seuil_valeur:
            # Vérifier qu'on n'a pas déjà généré une alerte récente
            alerte_recente = Alerte.objects.filter(
                regle=regle,
                cree_le__gte=depuis
            ).exists()
            
            if not alerte_recente:
                message = regle.message_template.format(
                    titre=f"Seuil d'événements atteint",
                    description=f"{nombre} événements en {regle.periode_minutes} minutes",
                    valeur=nombre,
                    seuil=regle.seuil_valeur
                )
                
                alerte = self.alerte_service.creer_alerte(
                    titre=f"Alerte: {regle.nom}",
                    message=message,
                    priorite=regle.priorite,
                    departement_id=regle.departement_id,
                    regle_id=regle.id,
                    donnees_contexte={'nombre_evenements': nombre}
                )
                return [alerte]
        
        return []
    
    def _evaluer_seuil_temps(self, regle: RegleAlerte) -> List[Alerte]:
        """Évalue le seuil de temps de workflow."""
        # TODO: Implémenter
        return []
    
    def _evaluer_evenement_critique(self, regle: RegleAlerte) -> List[Alerte]:
        """Génère des alertes pour les événements critiques."""
        # Les événements critiques génèrent automatiquement des alertes
        evenements = MicroEvenement.objects.filter(
            severite='CRITIQUE',
            statut='SIGNALE'
        ).exclude(
            alertes__isnull=False
        )
        
        if regle.departement:
            evenements = evenements.filter(departement=regle.departement)
        
        alertes = []
        for event in evenements:
            alerte = self.alerte_service.creer_alerte(
                titre=f"Événement critique: {event.titre}",
                message=event.description,
                priorite='URGENTE',
                departement_id=event.departement_id,
                regle_id=regle.id,
                evenement_id=event.id
            )
            alertes.append(alerte)
        
        return alertes
    
    def _evaluer_goulot_detecte(self, regle: RegleAlerte) -> List[Alerte]:
        """Génère des alertes pour les nouveaux goulots."""
        goulots = AnalyseGoulotEtranglement.objects.filter(
            statut='DETECTE',
            gravite__in=['ELEVEE', 'CRITIQUE']
        ).exclude(
            alertes__isnull=False
        )
        
        if regle.departement:
            goulots = goulots.filter(departement=regle.departement)
        
        alertes = []
        for goulot in goulots:
            alerte = self.alerte_service.creer_alerte(
                titre=f"Goulot détecté: {goulot.titre}",
                message=goulot.description,
                priorite='HAUTE' if goulot.gravite == 'ELEVEE' else 'URGENTE',
                departement_id=goulot.departement_id,
                regle_id=regle.id,
                goulot_id=goulot.id
            )
            alertes.append(alerte)
        
        return alertes
    
    def _evaluer_workflow_retard(self, regle: RegleAlerte) -> List[Alerte]:
        """Génère des alertes pour les workflows en retard."""
        workflows_en_cours = InstanceWorkflow.objects.filter(
            statut__in=['INITIE', 'EN_COURS']
        )
        
        if regle.departement:
            workflows_en_cours = workflows_en_cours.filter(
                departement=regle.departement
            )
        
        if regle.type_workflow:
            workflows_en_cours = workflows_en_cours.filter(
                type_workflow=regle.type_workflow
            )
        
        alertes = []
        for workflow in workflows_en_cours:
            if workflow.est_en_retard:
                # Vérifier qu'on n'a pas déjà une alerte pour ce workflow
                alerte_existante = Alerte.objects.filter(
                    workflow=workflow,
                    statut__in=['NOUVELLE', 'VUE']
                ).exists()
                
                if not alerte_existante:
                    alerte = self.alerte_service.creer_alerte(
                        titre=f"Workflow en retard: {workflow.type_workflow.nom}",
                        message=f"Le workflow {workflow.reference_patient} dépasse le seuil d'alerte. "
                               f"Durée: {workflow.duree_ecoulee_minutes} minutes.",
                        priorite=regle.priorite,
                        departement_id=workflow.departement_id,
                        regle_id=regle.id,
                        workflow_id=workflow.id
                    )
                    alertes.append(alerte)
        
        return alertes
