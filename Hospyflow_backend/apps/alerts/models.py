from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class RegleAlerte(models.Model):
    """
    Règles configurables pour le déclenchement des alertes.
    Pattern Strategy: différentes règles pour différentes conditions.
    """
    
    class TypeRegle(models.TextChoices):
        SEUIL_EVENEMENTS = 'SEUIL_EVENEMENTS', _('Seuil d\'événements')
        SEUIL_TEMPS = 'SEUIL_TEMPS', _('Seuil de temps')
        EVENEMENT_CRITIQUE = 'EVENEMENT_CRITIQUE', _('Événement critique')
        GOULOT_DETECTE = 'GOULOT_DETECTE', _('Goulot détecté')
        WORKFLOW_RETARD = 'WORKFLOW_RETARD', _('Workflow en retard')
    
    class Priorite(models.TextChoices):
        BASSE = 'BASSE', _('Basse')
        NORMALE = 'NORMALE', _('Normale')
        HAUTE = 'HAUTE', _('Haute')
        URGENTE = 'URGENTE', _('Urgente')
    
    nom = models.CharField(_('Nom'), max_length=100)
    code = models.CharField(_('Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    type_regle = models.CharField(
        _('Type de règle'),
        max_length=30,
        choices=TypeRegle.choices
    )
    
    # Configuration de la règle
    seuil_valeur = models.PositiveIntegerField(
        _('Valeur seuil'),
        default=10,
        help_text=_('Valeur numérique pour le déclenchement')
    )
    periode_minutes = models.PositiveIntegerField(
        _('Période (minutes)'),
        default=60,
        help_text=_('Période d\'observation pour la règle')
    )
    
    # Cibles
    departement = models.ForeignKey(
        'accounts.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='regles_alerte',
        verbose_name=_('Département'),
        help_text=_('Laisser vide pour tous les départements')
    )
    type_workflow = models.ForeignKey(
        'workflows.TypeWorkflow',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='regles_alerte',
        verbose_name=_('Type de workflow')
    )
    
    # Alerte
    priorite = models.CharField(
        _('Priorité de l\'alerte'),
        max_length=20,
        choices=Priorite.choices,
        default=Priorite.NORMALE
    )
    message_template = models.TextField(
        _('Modèle de message'),
        default='{titre}: {description}',
        help_text=_('Utilisez {titre}, {description}, {valeur}, {seuil}')
    )
    
    # État
    est_actif = models.BooleanField(_('Actif'), default=True)
    cree_le = models.DateTimeField(_('Créé le'), auto_now_add=True)
    modifie_le = models.DateTimeField(_('Modifié le'), auto_now=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='regles_creees',
        verbose_name=_('Créé par')
    )
    
    class Meta:
        verbose_name = _('Règle d\'alerte')
        verbose_name_plural = _('Règles d\'alertes')
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_regle_display()})"


class Alerte(models.Model):
    """
    Alerte générée par le système.
    Notifications aux administrateurs pour les situations critiques.
    """
    
    class Statut(models.TextChoices):
        NOUVELLE = 'NOUVELLE', _('Nouvelle')
        VUE = 'VUE', _('Vue')
        ACQUITTEE = 'ACQUITTEE', _('Acquittée')
        RESOLUE = 'RESOLUE', _('Résolue')
        IGNOREE = 'IGNOREE', _('Ignorée')
    
    class Priorite(models.TextChoices):
        BASSE = 'BASSE', _('Basse')
        NORMALE = 'NORMALE', _('Normale')
        HAUTE = 'HAUTE', _('Haute')
        URGENTE = 'URGENTE', _('Urgente')
    
    # Règle source
    regle = models.ForeignKey(
        RegleAlerte,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes_generees',
        verbose_name=_('Règle source')
    )
    
    # Contenu
    titre = models.CharField(_('Titre'), max_length=200)
    message = models.TextField(_('Message'))
    priorite = models.CharField(
        _('Priorité'),
        max_length=20,
        choices=Priorite.choices,
        default=Priorite.NORMALE
    )
    statut = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.NOUVELLE
    )
    
    # Contexte
    departement = models.ForeignKey(
        'accounts.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes',
        verbose_name=_('Département')
    )
    
    # Liens vers les objets concernés
    evenement = models.ForeignKey(
        'events.MicroEvenement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes',
        verbose_name=_('Événement lié')
    )
    goulot = models.ForeignKey(
        'analytics.AnalyseGoulotEtranglement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes',
        verbose_name=_('Goulot lié')
    )
    workflow = models.ForeignKey(
        'workflows.InstanceWorkflow',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes',
        verbose_name=_('Workflow lié')
    )
    
    # Données additionnelles
    donnees_contexte = models.JSONField(
        _('Données de contexte'),
        default=dict,
        blank=True
    )
    
    # Métadonnées
    cree_le = models.DateTimeField(_('Créé le'), auto_now_add=True)
    vue_le = models.DateTimeField(_('Vue le'), null=True, blank=True)
    acquittee_le = models.DateTimeField(_('Acquittée le'), null=True, blank=True)
    resolue_le = models.DateTimeField(_('Résolue le'), null=True, blank=True)
    
    acquittee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertes_acquittees',
        verbose_name=_('Acquittée par')
    )
    
    class Meta:
        verbose_name = _('Alerte')
        verbose_name_plural = _('Alertes')
        ordering = ['-cree_le']
        indexes = [
            models.Index(fields=['-cree_le', 'statut']),
            models.Index(fields=['priorite', 'statut']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.get_priorite_display()}"


class AbonnementAlerte(models.Model):
    """
    Abonnements des utilisateurs aux alertes.
    Permet de personnaliser les notifications reçues.
    """
    
    class CanalNotification(models.TextChoices):
        APP = 'APP', _('Application')
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
    
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='abonnements_alertes',
        verbose_name=_('Utilisateur')
    )
    
    # Filtres
    priorite_minimum = models.CharField(
        _('Priorité minimum'),
        max_length=20,
        choices=Alerte.Priorite.choices,
        default=Alerte.Priorite.NORMALE,
        help_text=_('Recevoir les alertes de cette priorité et supérieures')
    )
    departements = models.ManyToManyField(
        'accounts.Department',
        blank=True,
        related_name='abonnes_alertes',
        verbose_name=_('Départements'),
        help_text=_('Laisser vide pour tous les départements')
    )
    types_regles = models.ManyToManyField(
        RegleAlerte,
        blank=True,
        related_name='abonnes',
        verbose_name=_('Types de règles'),
        help_text=_('Laisser vide pour toutes les règles')
    )
    
    # Canaux
    canal = models.CharField(
        _('Canal de notification'),
        max_length=20,
        choices=CanalNotification.choices,
        default=CanalNotification.APP
    )
    
    # État
    est_actif = models.BooleanField(_('Actif'), default=True)
    cree_le = models.DateTimeField(_('Créé le'), auto_now_add=True)
    modifie_le = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Abonnement aux alertes')
        verbose_name_plural = _('Abonnements aux alertes')
        unique_together = ['utilisateur', 'canal']
    
    def __str__(self):
        return f"{self.utilisateur.email} - {self.get_canal_display()}"
