from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class TypeWorkflow(models.Model):
    """
    Types de workflows hospitaliers.
    Exemples: Admission patient, Examens de laboratoire, Urgences, etc.
    """
    
    class Categorie(models.TextChoices):
        ADMISSION = 'ADMISSION', _('Admission patient')
        LABORATOIRE = 'LABORATOIRE', _('Examens de laboratoire')
        URGENCE = 'URGENCE', _('Service des urgences')
        CHIRURGIE = 'CHIRURGIE', _('Bloc opératoire')
        RADIOLOGIE = 'RADIOLOGIE', _('Imagerie médicale')
        CONSULTATION = 'CONSULTATION', _('Consultation externe')
        HOSPITALISATION = 'HOSPITALISATION', _('Hospitalisation')
        SORTIE = 'SORTIE', _('Sortie patient')
    
    nom = models.CharField(_('Nom'), max_length=100)
    code = models.CharField(_('Code'), max_length=20, unique=True)
    categorie = models.CharField(
        _('Catégorie'),
        max_length=20,
        choices=Categorie.choices,
        default=Categorie.ADMISSION
    )
    description = models.TextField(_('Description'), blank=True)
    duree_standard_minutes = models.PositiveIntegerField(
        _('Durée standard (minutes)'),
        default=60,
        help_text=_('Durée attendue pour compléter ce type de workflow')
    )
    seuil_alerte_minutes = models.PositiveIntegerField(
        _('Seuil d\'alerte (minutes)'),
        default=90,
        help_text=_('Durée au-delà de laquelle une alerte est déclenchée')
    )
    est_actif = models.BooleanField(_('Actif'), default=True)
    ordre_affichage = models.PositiveIntegerField(_('Ordre d\'affichage'), default=0)
    cree_le = models.DateTimeField(_('Créé le'), auto_now_add=True)
    modifie_le = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Type de workflow')
        verbose_name_plural = _('Types de workflows')
        ordering = ['ordre_affichage', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"


class EtapeWorkflow(models.Model):
    """
    Étapes individuelles au sein d'un workflow.
    Chaque type de workflow contient plusieurs étapes ordonnées.
    """
    
    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', _('En attente')
        EN_COURS = 'EN_COURS', _('En cours')
        TERMINE = 'TERMINE', _('Terminé')
        BLOQUE = 'BLOQUE', _('Bloqué')
        ANNULE = 'ANNULE', _('Annulé')
    
    type_workflow = models.ForeignKey(
        TypeWorkflow,
        on_delete=models.CASCADE,
        related_name='etapes',
        verbose_name=_('Type de workflow')
    )
    nom = models.CharField(_('Nom de l\'étape'), max_length=100)
    code = models.CharField(_('Code'), max_length=20)
    description = models.TextField(_('Description'), blank=True)
    ordre = models.PositiveIntegerField(_('Ordre'), default=0)
    duree_estimee_minutes = models.PositiveIntegerField(
        _('Durée estimée (minutes)'),
        default=15
    )
    est_obligatoire = models.BooleanField(_('Obligatoire'), default=True)
    departement_responsable = models.ForeignKey(
        'accounts.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etapes_responsables',
        verbose_name=_('Département responsable')
    )
    
    class Meta:
        verbose_name = _('Étape de workflow')
        verbose_name_plural = _('Étapes de workflows')
        ordering = ['type_workflow', 'ordre']
        unique_together = ['type_workflow', 'code']
    
    def __str__(self):
        return f"{self.type_workflow.nom} - {self.nom}"


class InstanceWorkflow(models.Model):
    """
    Instance active d'un workflow pour un patient/cas spécifique.
    Permet le suivi en temps réel du parcours.
    """
    
    class Statut(models.TextChoices):
        INITIE = 'INITIE', _('Initié')
        EN_COURS = 'EN_COURS', _('En cours')
        EN_PAUSE = 'EN_PAUSE', _('En pause')
        TERMINE = 'TERMINE', _('Terminé')
        ABANDONNE = 'ABANDONNE', _('Abandonné')
    
    class Priorite(models.TextChoices):
        BASSE = 'BASSE', _('Basse')
        NORMALE = 'NORMALE', _('Normale')
        HAUTE = 'HAUTE', _('Haute')
        URGENTE = 'URGENTE', _('Urgente')
        CRITIQUE = 'CRITIQUE', _('Critique')
    
    type_workflow = models.ForeignKey(
        TypeWorkflow,
        on_delete=models.PROTECT,
        related_name='instances',
        verbose_name=_('Type de workflow')
    )
    reference_patient = models.CharField(
        _('Référence patient'),
        max_length=50,
        help_text=_('Identifiant anonymisé du patient')
    )
    etape_actuelle = models.ForeignKey(
        EtapeWorkflow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instances_actuelles',
        verbose_name=_('Étape actuelle')
    )
    statut = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.INITIE
    )
    priorite = models.CharField(
        _('Priorité'),
        max_length=20,
        choices=Priorite.choices,
        default=Priorite.NORMALE
    )
    departement = models.ForeignKey(
        'accounts.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='instances_workflow',
        verbose_name=_('Département')
    )
    initie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='workflows_inities',
        verbose_name=_('Initié par')
    )
    notes = models.TextField(_('Notes'), blank=True)
    demarre_le = models.DateTimeField(_('Démarré le'), auto_now_add=True)
    termine_le = models.DateTimeField(_('Terminé le'), null=True, blank=True)
    modifie_le = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Instance de workflow')
        verbose_name_plural = _('Instances de workflows')
        ordering = ['-demarre_le']
    
    def __str__(self):
        return f"{self.type_workflow.nom} - {self.reference_patient} ({self.get_statut_display()})"
    
    @property
    def est_en_retard(self):
        """Vérifie si le workflow dépasse la durée standard."""
        from django.utils import timezone
        if self.statut in [self.Statut.TERMINE, self.Statut.ABANDONNE]:
            return False
        duree = (timezone.now() - self.demarre_le).total_seconds() / 60
        return duree > self.type_workflow.seuil_alerte_minutes
    
    @property
    def duree_ecoulee_minutes(self):
        """Calcule la durée écoulée depuis le début."""
        from django.utils import timezone
        fin = self.termine_le or timezone.now()
        return int((fin - self.demarre_le).total_seconds() / 60)


class TransitionEtape(models.Model):
    """
    Enregistrement des transitions entre étapes d'un workflow.
    Permet l'analyse des temps de passage et des blocages.
    """
    
    instance = models.ForeignKey(
        InstanceWorkflow,
        on_delete=models.CASCADE,
        related_name='transitions',
        verbose_name=_('Instance de workflow')
    )
    etape_source = models.ForeignKey(
        EtapeWorkflow,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transitions_sortantes',
        verbose_name=_('Étape source')
    )
    etape_destination = models.ForeignKey(
        EtapeWorkflow,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transitions_entrantes',
        verbose_name=_('Étape destination')
    )
    effectuee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transitions_effectuees',
        verbose_name=_('Effectuée par')
    )
    horodatage = models.DateTimeField(_('Horodatage'), auto_now_add=True)
    duree_etape_minutes = models.PositiveIntegerField(
        _('Durée de l\'étape (minutes)'),
        null=True,
        blank=True
    )
    commentaire = models.TextField(_('Commentaire'), blank=True)
    
    class Meta:
        verbose_name = _('Transition d\'étape')
        verbose_name_plural = _('Transitions d\'étapes')
        ordering = ['instance', 'horodatage']
    
    def __str__(self):
        source = self.etape_source.nom if self.etape_source else "Début"
        dest = self.etape_destination.nom if self.etape_destination else "Fin"
        return f"{source} → {dest}"
