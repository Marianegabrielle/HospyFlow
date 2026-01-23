from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class CategorieEvenement(models.Model):
    """
    Catégories de micro-événements.
    Permet de classifier les types de retards et problèmes.
    """
    
    class TypeCategorie(models.TextChoices):
        RETARD = 'RETARD', _('Retard')
        BLOCAGE = 'BLOCAGE', _('Blocage')
        EQUIPEMENT = 'EQUIPEMENT', _('Problème d\'équipement')
        COORDINATION = 'COORDINATION', _('Problème de coordination')
        RESSOURCE = 'RESSOURCE', _('Manque de ressources')
        PATIENT = 'PATIENT', _('Lié au patient')
        AUTRE = 'AUTRE', _('Autre')
    
    nom = models.CharField(_('Nom'), max_length=100)
    code = models.CharField(_('Code'), max_length=20, unique=True)
    type_categorie = models.CharField(
        _('Type'),
        max_length=20,
        choices=TypeCategorie.choices,
        default=TypeCategorie.RETARD
    )
    description = models.TextField(_('Description'), blank=True)
    icone = models.CharField(_('Icône'), max_length=50, blank=True)
    couleur = models.CharField(
        _('Couleur'),
        max_length=7,
        default='#FFA500',
        help_text=_('Code couleur hexadécimal')
    )
    est_actif = models.BooleanField(_('Actif'), default=True)
    ordre_affichage = models.PositiveIntegerField(_('Ordre'), default=0)
    
    class Meta:
        verbose_name = _('Catégorie d\'événement')
        verbose_name_plural = _('Catégories d\'événements')
        ordering = ['ordre_affichage', 'nom']
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_categorie_display()})"


class MicroEvenement(models.Model):
    """
    Micro-événement signalé par le personnel hospitalier.
    Représente un retard, blocage ou incident dans un workflow.
    """
    
    class Severite(models.TextChoices):
        FAIBLE = 'FAIBLE', _('Faible')
        MOYEN = 'MOYEN', _('Moyen')
        ELEVE = 'ELEVE', _('Élevé')
        CRITIQUE = 'CRITIQUE', _('Critique')
    
    class Statut(models.TextChoices):
        SIGNALE = 'SIGNALE', _('Signalé')
        EN_COURS = 'EN_COURS', _('En cours de traitement')
        RESOLU = 'RESOLU', _('Résolu')
        IGNORE = 'IGNORE', _('Ignoré')
    
    # Relations
    rapporteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evenements_rapportes',
        verbose_name=_('Rapporteur')
    )
    departement = models.ForeignKey(
        'accounts.Department',
        on_delete=models.SET_NULL,
        null=True,
        related_name='evenements',
        verbose_name=_('Département')
    )
    instance_workflow = models.ForeignKey(
        'workflows.InstanceWorkflow',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evenements',
        verbose_name=_('Instance de workflow')
    )
    categorie = models.ForeignKey(
        CategorieEvenement,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evenements',
        verbose_name=_('Catégorie')
    )
    
    # Informations de l'événement
    titre = models.CharField(_('Titre'), max_length=200)
    description = models.TextField(_('Description'))
    severite = models.CharField(
        _('Sévérité'),
        max_length=20,
        choices=Severite.choices,
        default=Severite.MOYEN
    )
    statut = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.SIGNALE
    )
    
    # Estimation du retard
    delai_estime_minutes = models.PositiveIntegerField(
        _('Délai estimé (minutes)'),
        null=True,
        blank=True,
        help_text=_('Impact estimé en minutes sur le workflow')
    )
    
    # Localisation
    lieu = models.CharField(
        _('Lieu'),
        max_length=100,
        blank=True,
        help_text=_('Emplacement précis de l\'événement')
    )
    
    # Horodatage
    survenu_le = models.DateTimeField(
        _('Survenu le'),
        help_text=_('Date et heure de survenue de l\'événement')
    )
    signale_le = models.DateTimeField(_('Signalé le'), auto_now_add=True)
    resolu_le = models.DateTimeField(_('Résolu le'), null=True, blank=True)
    modifie_le = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    # Résolution
    resolu_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evenements_resolus',
        verbose_name=_('Résolu par')
    )
    commentaire_resolution = models.TextField(
        _('Commentaire de résolution'),
        blank=True
    )
    
    # Métadonnées
    est_recurrent = models.BooleanField(
        _('Récurrent'),
        default=False,
        help_text=_('Indique si ce type d\'événement se répète fréquemment')
    )
    
    class Meta:
        verbose_name = _('Micro-événement')
        verbose_name_plural = _('Micro-événements')
        ordering = ['-signale_le']
        indexes = [
            models.Index(fields=['-signale_le']),
            models.Index(fields=['departement', 'statut']),
            models.Index(fields=['severite', 'statut']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.get_severite_display()} ({self.get_statut_display()})"
    
    @property
    def est_resolu(self):
        return self.statut == self.Statut.RESOLU
    
    @property
    def duree_resolution_minutes(self):
        """Calcule la durée entre le signalement et la résolution."""
        if self.resolu_le and self.signale_le:
            return int((self.resolu_le - self.signale_le).total_seconds() / 60)
        return None


class PieceJointeEvenement(models.Model):
    """Pièces jointes associées aux micro-événements."""
    
    class TypeFichier(models.TextChoices):
        IMAGE = 'IMAGE', _('Image')
        DOCUMENT = 'DOCUMENT', _('Document')
        AUDIO = 'AUDIO', _('Audio')
    
    evenement = models.ForeignKey(
        MicroEvenement,
        on_delete=models.CASCADE,
        related_name='pieces_jointes',
        verbose_name=_('Événement')
    )
    fichier = models.FileField(
        _('Fichier'),
        upload_to='evenements/pieces_jointes/'
    )
    type_fichier = models.CharField(
        _('Type'),
        max_length=20,
        choices=TypeFichier.choices,
        default=TypeFichier.IMAGE
    )
    nom_original = models.CharField(_('Nom original'), max_length=255)
    ajoute_le = models.DateTimeField(_('Ajouté le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Pièce jointe')
        verbose_name_plural = _('Pièces jointes')
    
    def __str__(self):
        return self.nom_original


class CommentaireEvenement(models.Model):
    """Commentaires et suivi des micro-événements."""
    
    evenement = models.ForeignKey(
        MicroEvenement,
        on_delete=models.CASCADE,
        related_name='commentaires',
        verbose_name=_('Événement')
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commentaires_evenements',
        verbose_name=_('Auteur')
    )
    contenu = models.TextField(_('Contenu'))
    cree_le = models.DateTimeField(_('Créé le'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Commentaire')
        verbose_name_plural = _('Commentaires')
        ordering = ['cree_le']
    
    def __str__(self):
        return f"Commentaire de {self.auteur} - {self.cree_le}"
