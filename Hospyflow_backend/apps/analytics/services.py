"""
Service Pattern - Moteur d'analyse et détection des goulots d'étranglement.
Implémente le pattern Observer pour la détection automatique.
"""
from typing import Dict, Any, List, Optional
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Avg, Q, F
from datetime import timedelta
from decimal import Decimal

from .models import AnalyseGoulotEtranglement, MetriqueDepartement, StatistiqueGlobale
from apps.workflows.models import InstanceWorkflow, TransitionEtape
from apps.events.models import MicroEvenement
from apps.accounts.models import Department, User


class AnalyseException(Exception):
    """Exception pour les erreurs d'analyse."""
    pass


class MoteurAnalyseService:
    """
    Moteur principal d'analyse des flux hospitaliers.
    Implémente le pattern Singleton pour une instance unique.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def detecter_goulots_etranglement(
        self,
        departement_id: Optional[int] = None,
        jours: int = 7
    ) -> List[AnalyseGoulotEtranglement]:
        """
        Détecte les goulots d'étranglement sur une période.
        
        Args:
            departement_id: Filtrer par département (optionnel)
            jours: Nombre de jours à analyser
        
        Returns:
            Liste des goulots détectés
        """
        periode_debut = timezone.now() - timedelta(days=jours)
        periode_fin = timezone.now()
        
        goulots_detectes = []
        
        # Analyser les étapes avec temps de passage anormal
        goulots_etapes = self._analyser_temps_etapes(
            periode_debut, periode_fin, departement_id
        )
        goulots_detectes.extend(goulots_etapes)
        
        # Analyser les concentrations d'événements
        goulots_evenements = self._analyser_concentrations_evenements(
            periode_debut, periode_fin, departement_id
        )
        goulots_detectes.extend(goulots_evenements)
        
        return goulots_detectes
    
    def _analyser_temps_etapes(
        self,
        debut,
        fin,
        departement_id: Optional[int]
    ) -> List[AnalyseGoulotEtranglement]:
        """Analyse les temps de passage par étape."""
        # Calculer les temps moyens par étape
        transitions = TransitionEtape.objects.filter(
            horodatage__gte=debut,
            horodatage__lte=fin,
            duree_etape_minutes__isnull=False
        )
        
        if departement_id:
            transitions = transitions.filter(
                instance__departement_id=departement_id
            )
        
        temps_par_etape = transitions.values(
            'etape_source__id',
            'etape_source__nom',
            'etape_source__type_workflow__id',
            'etape_source__type_workflow__nom',
            'etape_source__duree_estimee_minutes',
            'instance__departement__id',
            'instance__departement__name'
        ).annotate(
            duree_moyenne=Avg('duree_etape_minutes'),
            occurrences=Count('id')
        ).filter(
            occurrences__gte=5  # Minimum 5 occurrences pour analyse
        )
        
        goulots = []
        for data in temps_par_etape:
            duree_estimee = data.get('etape_source__duree_estimee_minutes', 15)
            duree_moyenne = data.get('duree_moyenne', 0)
            
            # Détecter si temps moyen > 150% du temps estimé
            if duree_moyenne and duree_moyenne > duree_estimee * 1.5:
                gravite = self._calculer_gravite_temps(duree_moyenne, duree_estimee)
                
                goulot = AnalyseGoulotEtranglement.objects.create(
                    departement_id=data.get('instance__departement__id'),
                    type_workflow_id=data.get('etape_source__type_workflow__id'),
                    etape_concernee_id=data.get('etape_source__id'),
                    titre=f"Ralentissement à l'étape: {data.get('etape_source__nom')}",
                    description=f"L'étape '{data.get('etape_source__nom')}' du workflow "
                               f"'{data.get('etape_source__type_workflow__nom')}' présente "
                               f"un temps moyen de {int(duree_moyenne)} minutes "
                               f"(estimé: {duree_estimee} minutes).",
                    gravite=gravite,
                    delai_moyen_minutes=int(duree_moyenne),
                    nombre_occurrences=data.get('occurrences', 1),
                    periode_debut=debut,
                    periode_fin=fin,
                    recommandations=self._generer_recommandations_temps(
                        duree_moyenne, duree_estimee
                    )
                )
                goulots.append(goulot)
        
        return goulots
    
    def _analyser_concentrations_evenements(
        self,
        debut,
        fin,
        departement_id: Optional[int]
    ) -> List[AnalyseGoulotEtranglement]:
        """Analyse les concentrations d'événements par lieu/département."""
        evenements = MicroEvenement.objects.filter(
            signale_le__gte=debut,
            signale_le__lte=fin
        )
        
        if departement_id:
            evenements = evenements.filter(departement_id=departement_id)
        
        # Grouper par département et catégorie
        concentrations = evenements.values(
            'departement__id',
            'departement__name',
            'categorie__nom'
        ).annotate(
            total=Count('id'),
            critiques=Count('id', filter=Q(severite='CRITIQUE')),
            delai_total=Avg('delai_estime_minutes')
        ).filter(
            total__gte=10  # Minimum 10 événements
        )
        
        goulots = []
        for data in concentrations:
            if data.get('total', 0) >= 10 or data.get('critiques', 0) >= 3:
                gravite = self._calculer_gravite_evenements(
                    data.get('total', 0),
                    data.get('critiques', 0)
                )
                
                goulot = AnalyseGoulotEtranglement.objects.create(
                    departement_id=data.get('departement__id'),
                    titre=f"Concentration d'événements: {data.get('categorie__nom')}",
                    description=f"Le département '{data.get('departement__name')}' "
                               f"enregistre {data.get('total')} événements de type "
                               f"'{data.get('categorie__nom')}' dont {data.get('critiques')} critiques.",
                    gravite=gravite,
                    delai_moyen_minutes=int(data.get('delai_total') or 0),
                    nombre_occurrences=data.get('total'),
                    periode_debut=debut,
                    periode_fin=fin,
                    recommandations=self._generer_recommandations_evenements(
                        data.get('categorie__nom'),
                        data.get('total'),
                        data.get('critiques')
                    )
                )
                goulots.append(goulot)
        
        return goulots
    
    def _calculer_gravite_temps(
        self,
        duree_moyenne: float,
        duree_estimee: int
    ) -> str:
        """Calcule la gravité basée sur le dépassement de temps."""
        ratio = duree_moyenne / duree_estimee if duree_estimee > 0 else 1
        
        if ratio >= 3:
            return 'CRITIQUE'
        elif ratio >= 2:
            return 'ELEVEE'
        elif ratio >= 1.5:
            return 'MODEREE'
        else:
            return 'FAIBLE'
    
    def _calculer_gravite_evenements(
        self,
        total: int,
        critiques: int
    ) -> str:
        """Calcule la gravité basée sur les événements."""
        if critiques >= 5:
            return 'CRITIQUE'
        elif critiques >= 3 or total >= 25:
            return 'ELEVEE'
        elif total >= 15:
            return 'MODEREE'
        else:
            return 'FAIBLE'
    
    def _generer_recommandations_temps(
        self,
        duree_moyenne: float,
        duree_estimee: int
    ) -> str:
        """Génère des recommandations pour les problèmes de temps."""
        recommandations = []
        
        if duree_moyenne > duree_estimee * 2:
            recommandations.append(
                "• Revoir le processus de cette étape et identifier les tâches redondantes"
            )
            recommandations.append(
                "• Envisager l'ajout de personnel supplémentaire"
            )
        
        recommandations.append(
            "• Analyser les causes de retard les plus fréquentes"
        )
        recommandations.append(
            "• Former le personnel sur les procédures optimisées"
        )
        
        return "\n".join(recommandations)
    
    def _generer_recommandations_evenements(
        self,
        categorie: str,
        total: int,
        critiques: int
    ) -> str:
        """Génère des recommandations pour les concentrations d'événements."""
        recommandations = [
            f"• Analyser en détail les {total} événements de type '{categorie}'",
            "• Identifier les causes racines communes",
            "• Mettre en place des actions préventives"
        ]
        
        if critiques > 0:
            recommandations.insert(
                0,
                f"• PRIORITÉ: Traiter les {critiques} événements critiques"
            )
        
        return "\n".join(recommandations)


class TableauBordService:
    """
    Service pour la génération des données du tableau de bord.
    Agrège les métriques pour les administrateurs.
    """
    
    def obtenir_donnees_tableau_bord(self) -> Dict[str, Any]:
        """
        Génère les données complètes du tableau de bord.
        
        Returns:
            Dict avec toutes les métriques du tableau de bord
        """
        maintenant = timezone.now()
        debut_journee = maintenant.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return {
            'resume': self._obtenir_resume(),
            'workflows': self._obtenir_stats_workflows(debut_journee),
            'evenements': self._obtenir_stats_evenements(debut_journee),
            'goulots': self._obtenir_stats_goulots(),
            'departements': self._obtenir_stats_departements(),
            'tendances': self._obtenir_tendances(7)
        }
    
    def _obtenir_resume(self) -> Dict[str, Any]:
        """Résumé global."""
        workflows_actifs = InstanceWorkflow.objects.filter(
            statut__in=['INITIE', 'EN_COURS', 'EN_PAUSE']
        ).count()
        
        evenements_ouverts = MicroEvenement.objects.filter(
            statut__in=['SIGNALE', 'EN_COURS']
        ).count()
        
        evenements_critiques = MicroEvenement.objects.filter(
            statut__in=['SIGNALE', 'EN_COURS'],
            severite='CRITIQUE'
        ).count()
        
        goulots_actifs = AnalyseGoulotEtranglement.objects.filter(
            statut__in=['DETECTE', 'EN_ANALYSE', 'CONFIRME']
        ).count()
        
        personnel_en_service = User.objects.filter(
            is_on_duty=True,
            is_active=True
        ).count()
        
        return {
            'workflows_actifs': workflows_actifs,
            'evenements_ouverts': evenements_ouverts,
            'evenements_critiques': evenements_critiques,
            'goulots_actifs': goulots_actifs,
            'personnel_en_service': personnel_en_service
        }
    
    def _obtenir_stats_workflows(self, debut_journee) -> Dict[str, Any]:
        """Statistiques des workflows."""
        workflows_jour = InstanceWorkflow.objects.filter(
            demarre_le__gte=debut_journee
        )
        
        return {
            'demarres_aujourdhui': workflows_jour.count(),
            'termines_aujourdhui': workflows_jour.filter(statut='TERMINE').count(),
            'en_retard': sum(1 for w in InstanceWorkflow.objects.filter(
                statut__in=['INITIE', 'EN_COURS']
            ) if w.est_en_retard)
        }
    
    def _obtenir_stats_evenements(self, debut_journee) -> Dict[str, Any]:
        """Statistiques des événements."""
        return {
            'signales_aujourdhui': MicroEvenement.objects.filter(
                signale_le__gte=debut_journee
            ).count(),
            'resolus_aujourdhui': MicroEvenement.objects.filter(
                resolu_le__gte=debut_journee
            ).count(),
            'par_severite': {
                'critique': MicroEvenement.objects.filter(
                    statut__in=['SIGNALE', 'EN_COURS'], severite='CRITIQUE'
                ).count(),
                'eleve': MicroEvenement.objects.filter(
                    statut__in=['SIGNALE', 'EN_COURS'], severite='ELEVE'
                ).count(),
                'moyen': MicroEvenement.objects.filter(
                    statut__in=['SIGNALE', 'EN_COURS'], severite='MOYEN'
                ).count(),
                'faible': MicroEvenement.objects.filter(
                    statut__in=['SIGNALE', 'EN_COURS'], severite='FAIBLE'
                ).count()
            }
        }
    
    def _obtenir_stats_goulots(self) -> Dict[str, Any]:
        """Statistiques des goulots."""
        goulots = AnalyseGoulotEtranglement.objects.filter(
            statut__in=['DETECTE', 'EN_ANALYSE', 'CONFIRME']
        )
        
        return {
            'total_actifs': goulots.count(),
            'par_gravite': {
                'critique': goulots.filter(gravite='CRITIQUE').count(),
                'elevee': goulots.filter(gravite='ELEVEE').count(),
                'moderee': goulots.filter(gravite='MODEREE').count(),
                'faible': goulots.filter(gravite='FAIBLE').count()
            }
        }
    
    def _obtenir_stats_departements(self) -> List[Dict[str, Any]]:
        """Statistiques par département."""
        departements = Department.objects.filter(is_active=True)
        stats = []
        
        for dept in departements:
            workflows_actifs = InstanceWorkflow.objects.filter(
                departement=dept,
                statut__in=['INITIE', 'EN_COURS']
            ).count()
            
            evenements_ouverts = MicroEvenement.objects.filter(
                departement=dept,
                statut__in=['SIGNALE', 'EN_COURS']
            ).count()
            
            stats.append({
                'id': dept.id,
                'nom': dept.name,
                'code': dept.code,
                'workflows_actifs': workflows_actifs,
                'evenements_ouverts': evenements_ouverts,
                'personnel_en_service': dept.staff.filter(is_on_duty=True).count()
            })
        
        return stats
    
    def _obtenir_tendances(self, jours: int) -> List[Dict[str, Any]]:
        """Obtient les tendances sur plusieurs jours."""
        tendances = []
        maintenant = timezone.now()
        
        for i in range(jours):
            date_debut = (maintenant - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            date_fin = date_debut + timedelta(days=1)
            
            workflows = InstanceWorkflow.objects.filter(
                demarre_le__gte=date_debut,
                demarre_le__lt=date_fin
            )
            
            evenements = MicroEvenement.objects.filter(
                signale_le__gte=date_debut,
                signale_le__lt=date_fin
            )
            
            tendances.append({
                'date': date_debut.date().isoformat(),
                'workflows_demarres': workflows.count(),
                'workflows_termines': workflows.filter(statut='TERMINE').count(),
                'evenements_signales': evenements.count(),
                'evenements_critiques': evenements.filter(severite='CRITIQUE').count()
            })
        
        return list(reversed(tendances))
    
    @transaction.atomic
    def generer_statistiques_quotidiennes(self):
        """
        Génère et sauvegarde les statistiques quotidiennes.
        À exécuter via une tâche planifiée (cron).
        """
        aujourdhui = timezone.now().date()
        
        resume = self._obtenir_resume()
        
        StatistiqueGlobale.objects.update_or_create(
            date=aujourdhui,
            defaults={
                'total_workflows_actifs': resume['workflows_actifs'],
                'total_evenements_ouverts': resume['evenements_ouverts'],
                'total_evenements_critiques': resume['evenements_critiques'],
                'total_goulots_actifs': resume['goulots_actifs'],
                'personnel_total_en_service': resume['personnel_en_service']
            }
        )
        
        # Générer métriques par département
        for dept in Department.objects.filter(is_active=True):
            self._generer_metrique_departement(dept, aujourdhui)
    
    def _generer_metrique_departement(self, departement, date):
        """Génère les métriques pour un département."""
        debut_journee = timezone.datetime.combine(
            date, timezone.datetime.min.time()
        ).replace(tzinfo=timezone.get_current_timezone())
        fin_journee = debut_journee + timedelta(days=1)
        
        workflows = InstanceWorkflow.objects.filter(
            departement=departement,
            demarre_le__date=date
        )
        
        evenements = MicroEvenement.objects.filter(
            departement=departement,
            signale_le__date=date
        )
        
        MetriqueDepartement.objects.update_or_create(
            departement=departement,
            date=date,
            defaults={
                'workflows_demarre': workflows.count(),
                'workflows_termines': workflows.filter(statut='TERMINE').count(),
                'workflows_abandonnes': workflows.filter(statut='ABANDONNE').count(),
                'evenements_signales': evenements.count(),
                'evenements_resolus': evenements.filter(statut='RESOLU').count(),
                'evenements_critiques': evenements.filter(severite='CRITIQUE').count(),
                'personnel_en_service': departement.staff.filter(is_on_duty=True).count()
            }
        )
