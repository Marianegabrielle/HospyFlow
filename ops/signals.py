from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MicroEvenement
from hospyFlow_core.analytics_service import moteur_analyse

@receiver(post_save, sender=MicroEvenement)
def trigger_analysis(sender, instance, created, **kwargs):
    """
    Automatically triggers the analytics engine when a new micro-event is saved.
    """
    if created:
        moteur_analyse.analyser_evenement(instance)
