from django.contrib import admin
from .models import Alerte, RegleAlerte, AbonnementAlerte


@admin.register(RegleAlerte)
class RegleAlerteAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'code', 'type_regle', 'priorite',
        'seuil_valeur', 'periode_minutes', 'est_actif'
    ]
    list_filter = ['type_regle', 'priorite', 'est_actif', 'departement']
    search_fields = ['nom', 'code', 'description']
    ordering = ['nom']


@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'priorite', 'statut', 'departement',
        'cree_le', 'acquittee_par'
    ]
    list_filter = ['priorite', 'statut', 'departement', 'cree_le']
    search_fields = ['titre', 'message']
    readonly_fields = ['cree_le', 'vue_le', 'acquittee_le', 'resolue_le']
    ordering = ['-cree_le']


@admin.register(AbonnementAlerte)
class AbonnementAlerteAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'canal', 'priorite_minimum', 'est_actif'
    ]
    list_filter = ['canal', 'priorite_minimum', 'est_actif']
    search_fields = ['utilisateur__email']
    filter_horizontal = ['departements', 'types_regles']
