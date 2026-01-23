"""
Models pour les services hospitaliers.
Compatible avec l'ancien backend ops/ pour faciliter la migration.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceHospitalier(models.Model):
    """
    Service/département hospitalier.
    Mapping vers Department existant pour compatibilité.
    """
    
    class Etat(models.TextChoices):
        NORMAL = 'NORMAL', _('Normal')
        TENSION = 'TENSION', _('Tension')
    
    # Utilise le Department existant comme base
    department = models.OneToOneField(
        'accounts.Department',
        on_delete=models.CASCADE,
        related_name='service_info',
        verbose_name=_('Département')
    )
    
    etat = models.CharField(
        _('État'),
        max_length=20,
        choices=Etat.choices,
        default=Etat.NORMAL
    )
    
    saturation = models.PositiveIntegerField(
        _('Saturation (%)'),
        default=0,
        help_text=_('Pourcentage de saturation du service')
    )
    
    derniere_maj = models.DateTimeField(
        _('Dernière mise à jour'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('Service Hospitalier')
        verbose_name_plural = _('Services Hospitaliers')
        ordering = ['department__name']
    
    def __str__(self):
        return f"{self.department.name} ({self.get_etat_display()})"
    
    @property
    def nom(self):
        """Compatibilité avec ancien backend"""
        return self.department.name
    
    @property
    def localisation(self):
        """Compatibilité avec ancien backend"""
        return f"{self.department.building} - {self.department.floor}" if self.department.building else ""
    
    def calculer_saturation(self):
        """
        Calcule la saturation basée sur les événements actifs.
        """
        from apps.events.models import MicroEvenement
        from django.utils import timezone
        from datetime import timedelta
        
        # Événements des dernières 24h
        depuis = timezone.now() - timedelta(hours=24)
        evenements_recents = MicroEvenement.objects.filter(
            departement=self.department,
            signale_le__gte=depuis,
            statut__in=['SIGNALE', 'EN_COURS']
        )
        
        # Calcul simple : 10% par événement actif, max 100%
        count = evenements_recents.count()
        self.saturation = min(count * 10, 100)
        
        # Mise à jour de l'état
        if self.saturation >= 70:
            self.etat = self.Etat.TENSION
        else:
            self.etat = self.Etat.NORMAL
        
        self.save()
        return self.saturation
