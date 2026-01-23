"""
Service Pattern - Couche de logique métier pour les événements.
"""
from typing import Optional, Dict, Any, List
from django.utils import timezone
from django.db import transaction

from .models import MicroEvenement, CategorieEvenement, CommentaireEvenement
from .repositories import MicroEvenementRepository, CommentaireEvenementRepository


class EvenementException(Exception):
    """Exception personnalisée pour les erreurs d'événements."""
    pass


class GestionEvenementService:
    """
    Service principal pour la gestion des micro-événements.
    Implémente le pattern Strategy pour différentes severités.
    """
    
    def __init__(self):
        self.evenement_repo = MicroEvenementRepository()
        self.commentaire_repo = CommentaireEvenementRepository()
    
    @transaction.atomic
    def signaler_evenement(
        self,
        rapporteur,
        titre: str,
        description: str,
        departement_id: int,
        categorie_id: int,
        severite: str = 'MOYEN',
        survenu_le=None,
        delai_estime_minutes: Optional[int] = None,
        lieu: str = '',
        instance_workflow_id: Optional[int] = None
    ) -> MicroEvenement:
        """
        Signale un nouveau micro-événement.
        
        Args:
            rapporteur: Utilisateur qui signale l'événement
            titre: Titre court de l'événement
            description: Description détaillée
            departement_id: ID du département concerné
            categorie_id: ID de la catégorie
            severite: Niveau de sévérité
            survenu_le: Date/heure de survenue (défaut: maintenant)
            delai_estime_minutes: Impact estimé en minutes
            lieu: Emplacement précis
            instance_workflow_id: ID du workflow associé (optionnel)
        
        Returns:
            MicroEvenement: L'événement créé
        """
        if survenu_le is None:
            survenu_le = timezone.now()
        
        evenement = self.evenement_repo.creer({
            'rapporteur': rapporteur,
            'titre': titre,
            'description': description,
            'departement_id': departement_id,
            'categorie_id': categorie_id,
            'severite': severite,
            'statut': MicroEvenement.Statut.SIGNALE,
            'survenu_le': survenu_le,
            'delai_estime_minutes': delai_estime_minutes,
            'lieu': lieu,
            'instance_workflow_id': instance_workflow_id
        })
        
        # Déclencher des actions selon la sévérité (Strategy pattern)
        self._traiter_severite(evenement)
        
        return evenement
    
    def _traiter_severite(self, evenement: MicroEvenement):
        """
        Traite l'événement selon sa sévérité.
        Implémente le pattern Strategy.
        """
        strategies = {
            'CRITIQUE': self._traiter_critique,
            'ELEVE': self._traiter_eleve,
            'MOYEN': self._traiter_moyen,
            'FAIBLE': self._traiter_faible
        }
        
        strategy = strategies.get(evenement.severite, self._traiter_moyen)
        strategy(evenement)
    
    def _traiter_critique(self, evenement: MicroEvenement):
        """Traitement pour les événements critiques."""
        # TODO: Envoyer notification immédiate
        # TODO: Créer alerte pour les admins
        pass
    
    def _traiter_eleve(self, evenement: MicroEvenement):
        """Traitement pour les événements de sévérité élevée."""
        # TODO: Notifier le responsable du département
        pass
    
    def _traiter_moyen(self, evenement: MicroEvenement):
        """Traitement pour les événements de sévérité moyenne."""
        pass
    
    def _traiter_faible(self, evenement: MicroEvenement):
        """Traitement pour les événements de faible sévérité."""
        pass
    
    @transaction.atomic
    def resoudre_evenement(
        self,
        evenement_id: int,
        resolu_par,
        commentaire_resolution: str = ''
    ) -> MicroEvenement:
        """
        Marque un événement comme résolu.
        
        Args:
            evenement_id: ID de l'événement
            resolu_par: Utilisateur qui résout
            commentaire_resolution: Commentaire optionnel
        
        Returns:
            MicroEvenement: L'événement mis à jour
        """
        evenement = self.evenement_repo.obtenir_par_id(evenement_id)
        if not evenement:
            raise EvenementException("Événement introuvable.")
        
        if evenement.statut == MicroEvenement.Statut.RESOLU:
            raise EvenementException("Cet événement est déjà résolu.")
        
        evenement.statut = MicroEvenement.Statut.RESOLU
        evenement.resolu_par = resolu_par
        evenement.resolu_le = timezone.now()
        evenement.commentaire_resolution = commentaire_resolution
        evenement.save()
        
        return evenement
    
    def prendre_en_charge(
        self,
        evenement_id: int,
        utilisateur
    ) -> MicroEvenement:
        """Prend en charge un événement (passe en statut EN_COURS)."""
        evenement = self.evenement_repo.obtenir_par_id(evenement_id)
        if not evenement:
            raise EvenementException("Événement introuvable.")
        
        if evenement.statut != MicroEvenement.Statut.SIGNALE:
            raise EvenementException(
                "Seuls les événements signalés peuvent être pris en charge."
            )
        
        evenement.statut = MicroEvenement.Statut.EN_COURS
        evenement.save()
        
        # Ajouter un commentaire automatique
        self.commentaire_repo.creer(
            evenement_id=evenement.id,
            auteur=utilisateur,
            contenu=f"Pris en charge par {utilisateur.get_full_name()}"
        )
        
        return evenement
    
    def ajouter_commentaire(
        self,
        evenement_id: int,
        auteur,
        contenu: str
    ) -> CommentaireEvenement:
        """Ajoute un commentaire à un événement."""
        evenement = self.evenement_repo.obtenir_par_id(evenement_id)
        if not evenement:
            raise EvenementException("Événement introuvable.")
        
        return self.commentaire_repo.creer(
            evenement_id=evenement_id,
            auteur=auteur,
            contenu=contenu
        )
    
    def marquer_recurrent(self, evenement_id: int) -> MicroEvenement:
        """Marque un événement comme récurrent."""
        evenement = self.evenement_repo.obtenir_par_id(evenement_id)
        if not evenement:
            raise EvenementException("Événement introuvable.")
        
        evenement.est_recurrent = True
        evenement.save()
        return evenement
    
    def obtenir_statistiques_departement(
        self,
        departement_id: int
    ) -> Dict[str, Any]:
        """
        Calcule les statistiques d'événements pour un département.
        
        Returns:
            Dict contenant les statistiques
        """
        evenements = MicroEvenement.objects.filter(departement_id=departement_id)
        
        non_resolus = evenements.exclude(statut='RESOLU')
        resolus = evenements.filter(statut='RESOLU')
        
        return {
            'total': evenements.count(),
            'non_resolus': non_resolus.count(),
            'critiques': non_resolus.filter(severite='CRITIQUE').count(),
            'eleves': non_resolus.filter(severite='ELEVE').count(),
            'resolus_dernieres_24h': resolus.filter(
                resolu_le__gte=timezone.now() - timezone.timedelta(hours=24)
            ).count(),
            'delai_moyen_minutes': self.evenement_repo.calculer_delai_moyen_resolution()
        }
    
    def obtenir_tendances(self, jours: int = 7) -> List[Dict[str, Any]]:
        """
        Analyse les tendances sur les derniers jours.
        
        Returns:
            Liste de statistiques quotidiennes
        """
        tendances = []
        maintenant = timezone.now()
        
        for i in range(jours):
            date_debut = (maintenant - timezone.timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            date_fin = date_debut + timezone.timedelta(days=1)
            
            evenements_jour = MicroEvenement.objects.filter(
                signale_le__gte=date_debut,
                signale_le__lt=date_fin
            )
            
            tendances.append({
                'date': date_debut.date().isoformat(),
                'total': evenements_jour.count(),
                'critiques': evenements_jour.filter(severite='CRITIQUE').count(),
                'resolus': evenements_jour.filter(statut='RESOLU').count()
            })
        
        return list(reversed(tendances))
