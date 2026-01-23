"""
Modèles pour les rapports.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


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
