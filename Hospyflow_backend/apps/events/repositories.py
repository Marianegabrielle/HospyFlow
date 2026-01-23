"""
Repository Pattern - Couche d'accès aux données pour les événements.
"""
from typing import List, Optional
from django.db.models import QuerySet, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import MicroEvenement, CategorieEvenement, CommentaireEvenement


class CategorieEvenementRepository:
    """Repository pour les catégories d'événements."""
    
    @staticmethod
    def obtenir_toutes_actives() -> QuerySet[CategorieEvenement]:
        """Retourne toutes les catégories actives."""
        return CategorieEvenement.objects.filter(est_actif=True).order_by('ordre_affichage')
    
    @staticmethod
    def obtenir_par_type(type_categorie: str) -> QuerySet[CategorieEvenement]:
        """Retourne les catégories par type."""
        return CategorieEvenement.objects.filter(
            type_categorie=type_categorie,
            est_actif=True
        )


class MicroEvenementRepository:
    """Repository pour les micro-événements."""
    
    @staticmethod
    def creer(donnees: dict) -> MicroEvenement:
        """Crée un nouveau micro-événement."""
        return MicroEvenement.objects.create(**donnees)
    
    @staticmethod
    def obtenir_par_id(evenement_id: int) -> Optional[MicroEvenement]:
        """Retourne un événement par son ID."""
        try:
            return MicroEvenement.objects.select_related(
                'rapporteur', 'departement', 'categorie', 'instance_workflow'
            ).get(pk=evenement_id)
        except MicroEvenement.DoesNotExist:
            return None
    
    @staticmethod
    def obtenir_non_resolus() -> QuerySet[MicroEvenement]:
        """Retourne tous les événements non résolus."""
        return MicroEvenement.objects.filter(
            statut__in=['SIGNALE', 'EN_COURS']
        ).select_related('rapporteur', 'departement', 'categorie')
    
    @staticmethod
    def obtenir_par_departement(
        departement_id: int,
        inclure_resolus: bool = False
    ) -> QuerySet[MicroEvenement]:
        """Retourne les événements d'un département."""
        queryset = MicroEvenement.objects.filter(departement_id=departement_id)
        if not inclure_resolus:
            queryset = queryset.exclude(statut='RESOLU')
        return queryset.select_related('rapporteur', 'categorie')
    
    @staticmethod
    def obtenir_par_severite(severite: str) -> QuerySet[MicroEvenement]:
        """Retourne les événements par sévérité."""
        return MicroEvenement.objects.filter(
            severite=severite
        ).exclude(statut='RESOLU')
    
    @staticmethod
    def obtenir_critiques() -> QuerySet[MicroEvenement]:
        """Retourne les événements critiques non résolus."""
        return MicroEvenement.objects.filter(
            severite='CRITIQUE',
            statut__in=['SIGNALE', 'EN_COURS']
        ).select_related('rapporteur', 'departement')
    
    @staticmethod
    def obtenir_par_rapporteur(utilisateur_id: int) -> QuerySet[MicroEvenement]:
        """Retourne les événements signalés par un utilisateur."""
        return MicroEvenement.objects.filter(
            rapporteur_id=utilisateur_id
        ).order_by('-signale_le')
    
    @staticmethod
    def obtenir_recents(heures: int = 24) -> QuerySet[MicroEvenement]:
        """Retourne les événements des dernières heures."""
        depuis = timezone.now() - timedelta(hours=heures)
        return MicroEvenement.objects.filter(
            signale_le__gte=depuis
        ).select_related('rapporteur', 'departement', 'categorie')
    
    @staticmethod
    def compter_par_departement() -> QuerySet:
        """Compte les événements par département."""
        return MicroEvenement.objects.filter(
            statut__in=['SIGNALE', 'EN_COURS']
        ).values('departement__name').annotate(
            total=Count('id')
        ).order_by('-total')
    
    @staticmethod
    def compter_par_categorie() -> QuerySet:
        """Compte les événements par catégorie."""
        return MicroEvenement.objects.filter(
            statut__in=['SIGNALE', 'EN_COURS']
        ).values('categorie__nom').annotate(
            total=Count('id')
        ).order_by('-total')
    
    @staticmethod
    def calculer_delai_moyen_resolution() -> Optional[float]:
        """Calcule le délai moyen de résolution en minutes."""
        from django.db.models import F, ExpressionWrapper, DurationField
        
        resolus = MicroEvenement.objects.filter(
            statut='RESOLU',
            resolu_le__isnull=False
        ).annotate(
            duree=ExpressionWrapper(
                F('resolu_le') - F('signale_le'),
                output_field=DurationField()
            )
        )
        
        if resolus.exists():
            total = sum((e.resolu_le - e.signale_le).total_seconds() for e in resolus)
            return total / resolus.count() / 60
        return None
    
    @staticmethod
    def rechercher(
        terme: str,
        departement_id: Optional[int] = None,
        categorie_id: Optional[int] = None,
        severite: Optional[str] = None,
        statut: Optional[str] = None,
        date_debut=None,
        date_fin=None
    ) -> QuerySet[MicroEvenement]:
        """Recherche avancée d'événements."""
        queryset = MicroEvenement.objects.all()
        
        if terme:
            queryset = queryset.filter(
                Q(titre__icontains=terme) |
                Q(description__icontains=terme) |
                Q(lieu__icontains=terme)
            )
        
        if departement_id:
            queryset = queryset.filter(departement_id=departement_id)
        
        if categorie_id:
            queryset = queryset.filter(categorie_id=categorie_id)
        
        if severite:
            queryset = queryset.filter(severite=severite)
        
        if statut:
            queryset = queryset.filter(statut=statut)
        
        if date_debut:
            queryset = queryset.filter(signale_le__gte=date_debut)
        
        if date_fin:
            queryset = queryset.filter(signale_le__lte=date_fin)
        
        return queryset.select_related('rapporteur', 'departement', 'categorie')


class CommentaireEvenementRepository:
    """Repository pour les commentaires d'événements."""
    
    @staticmethod
    def creer(evenement_id: int, auteur, contenu: str) -> CommentaireEvenement:
        """Crée un nouveau commentaire."""
        return CommentaireEvenement.objects.create(
            evenement_id=evenement_id,
            auteur=auteur,
            contenu=contenu
        )
    
    @staticmethod
    def obtenir_par_evenement(evenement_id: int) -> QuerySet[CommentaireEvenement]:
        """Retourne les commentaires d'un événement."""
        return CommentaireEvenement.objects.filter(
            evenement_id=evenement_id
        ).select_related('auteur')
