from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class AnalyseGoulotEtranglement(models.Model):
    """
    Analyse de goulot d'étranglement détecté dans les workflows.
    Pattern Observer: les analyses sont générées automatiquement.
    """
    
    class Statut(models.TextChoices):
        DETECTE = 'DETECTE', _('Détecté')
        EN_ANALYSE = 'EN_ANALYSE', _('En analyse')
        CONFIRME = 'CONFIRME', _('Confirmé')
        RESOLU = 'RESOLU', _('Résolu')
        FAUX_POSITIF = 'FAUX_POSITIF', _('Faux positif')
    
    class Gravite(models.TextChoices):
        FAIBLE = 'FAIBLE', _('Faible')
        MODEREE = 'MODEREE', _('Modérée')
        ELEVEE = 'ELEVEE', _('Élevée')
        CRITIQUE = 'CRITIQUE', _('Critique')
    
    # Localisation du goulot
    departement = models.ForeignKey(
        'accounts.Department',
        on_delete=models.CASCADE,
        related_name='goulots',
        verbose_name=_('Département')
    )
    type_workflow = models.ForeignKey(
        'workflows.TypeWorkflow',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goulots',
        verbose_name=_('Type de workflow')
    )
    etape_concernee = models.ForeignKey(
        'workflows.EtapeWorkflow',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goulots',
        verbose_name=_('Étape concernée')
    )
    
    # Informations de l'analyse
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'))
    statut = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.DETECTE
    )
    gravite = models.CharField(
        _('Gravité'),
        max_length=20,
        choices=Gravite.choices,
        default=Gravite.MODEREE
    )
    
    # Métriques
    delai_moyen_minutes = models.PositiveIntegerField(
        _('Délai moyen (minutes)'),
        help_text=_('Temps moyen de blocage observé')
    )
    nombre_occurrences = models.PositiveIntegerField(
        _('Nombre d\'occurrences'),
        default=1
    )
    impact_patients = models.PositiveIntegerField(
        _('Patients impactés'),
        default=0
    )
    
    # Période d'analyse
    periode_debut = models.DateTimeField(_('Début de période'))
    periode_fin = models.DateTimeField(_('Fin de période'))
    
    # Recommandations
    recommandations = models.TextField(
        _('Recommandations'),
        blank=True,
        help_text=_('Actions recommandées pour résoudre le goulot')
    )
    
    # Métadonnées
    detecte_le = models.DateTimeField(_('Détecté le'), auto_now_add=True)
    confirme_le = models.DateTimeField(_('Confirmé le'), null=True, blank=True)
    resolu_le = models.DateTimeField(_('Résolu le'), null=True, blank=True)
    confirme_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goulots_confirmes',
        verbose_name=_('Confirmé par')
    )
    
    class Meta:
        verbose_name = _('Analyse de goulot d\'étranglement')
        verbose_name_plural = _('Analyses de goulots d\'étranglement')
        ordering = ['-detecte_le']
    
    def __str__(self):
        return f"{self.titre} - {self.get_gravite_display()}"


class MetriqueDepartement(models.Model):
    """
    Métriques agrégées par département et par période.
    Permet le suivi des KPIs opérationnels.
    """
    
    departement = models.ForeignKey(
        'accounts.Department',
        on_delete=models.CASCADE,
        related_name='metriques',
        verbose_name=_('Département')
    )
    date = models.DateField(_('Date'))
    
    # Métriques de workflow
    workflows_demarre = models.PositiveIntegerField(
        _('Workflows démarrés'),
        default=0
    )
    workflows_termines = models.PositiveIntegerField(
        _('Workflows terminés'),
        default=0
    )
    workflows_abandonnes = models.PositiveIntegerField(
        _('Workflows abandonnés'),
        default=0
    )
    duree_moyenne_workflow_minutes = models.PositiveIntegerField(
        _('Durée moyenne workflow (minutes)'),
        null=True,
        blank=True
    )
    
    # Métriques d'événements
    evenements_signales = models.PositiveIntegerField(
        _('Événements signalés'),
        default=0
    )
    evenements_resolus = models.PositiveIntegerField(
        _('Événements résolus'),
        default=0
    )
    evenements_critiques = models.PositiveIntegerField(
        _('Événements critiques'),
        default=0
    )
    delai_resolution_moyen_minutes = models.PositiveIntegerField(
        _('Délai résolution moyen (minutes)'),
        null=True,
        blank=True
    )
    
    # Métriques de charge
    personnel_en_service = models.PositiveIntegerField(
        _('Personnel en service'),
        default=0
    )
    
    # Scores
    score_efficacite = models.DecimalField(
        _('Score d\'efficacité'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Score de 0 à 100')
    )
    
    cree_le = models.DateTimeField(_('Créé le'), auto_now_add=True)
    modifie_le = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Métrique de département')
        verbose_name_plural = _('Métriques de départements')
        unique_together = ['departement', 'date']
        ordering = ['-date', 'departement']
    
    def __str__(self):
        return f"{self.departement.name} - {self.date}"


class StatistiqueGlobale(models.Model):
    """
    Statistiques globales de l'hôpital par jour.
    Vue d'ensemble pour le tableau de bord administrateur.
    """
    
    date = models.DateField(_('Date'), unique=True)
    
    # Totaux
    total_workflows_actifs = models.PositiveIntegerField(
        _('Workflows actifs'),
        default=0
    )
    total_workflows_termines = models.PositiveIntegerField(
        _('Workflows terminés (jour)'),
        default=0
    )
    total_evenements_ouverts = models.PositiveIntegerField(
        _('Événements ouverts'),
        default=0
    )
    total_evenements_critiques = models.PositiveIntegerField(
        _('Événements critiques'),
        default=0
    )
    total_goulots_actifs = models.PositiveIntegerField(
        _('Goulots actifs'),
        default=0
    )
    
    # Temps moyens
    temps_attente_moyen_minutes = models.PositiveIntegerField(
        _('Temps attente moyen (minutes)'),
        null=True,
        blank=True
    )
    temps_resolution_moyen_minutes = models.PositiveIntegerField(
        _('Temps résolution moyen (minutes)'),
        null=True,
        blank=True
    )
    
    # Scores
    score_global_efficacite = models.DecimalField(
        _('Score global d\'efficacité'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Personnel
    personnel_total_en_service = models.PositiveIntegerField(
        _('Personnel total en service'),
        default=0
    )
    
    cree_le = models.DateTimeField(_('Créé le'), auto_now_add=True)
    modifie_le = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Statistique globale')
        verbose_name_plural = _('Statistiques globales')
        ordering = ['-date']
    
    def __str__(self):
        return f"Statistiques {self.date}"


class Rapport(models.Model):
    """
    Rapport généré par le système.
    Compatible avec l'ancien backend ops/.
    """
    
    class Format(models.TextChoices):
        PDF = 'pdf', _('PDF')
        CSV = 'csv', _('CSV')
    
    plage_date = models.CharField(
        _('Plage de dates'),
        max_length=100,
        help_text=_('Ex: 2026-01-20 to 2026-01-27')
    )
    
    donnees_metriques = models.JSONField(
        _('Données métriques'),
        help_text=_('Statistiques agrégées')
    )
    
    format = models.CharField(
        _('Format'),
        max_length=10,
        choices=Format.choices,
        default=Format.PDF
    )
    
    fichier = models.FileField(
        _('Fichier'),
        upload_to='rapports/',
        null=True,
        blank=True
    )
    
    genere_le = models.DateTimeField(
        _('Généré le'),
        auto_now_add=True
    )
    
    genere_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rapports_generes',
        verbose_name=_('Généré par')
    )
    
    class Meta:
        verbose_name = _('Rapport')
        verbose_name_plural = _('Rapports')
        ordering = ['-genere_le']
    
    def __str__(self):
        return f"Rapport {self.plage_date} ({self.get_format_display()})"
