from django.contrib import admin
from .models import TypeWorkflow, EtapeWorkflow, InstanceWorkflow, TransitionEtape


class EtapeWorkflowInline(admin.TabularInline):
    model = EtapeWorkflow
    extra = 1
    ordering = ['ordre']


@admin.register(TypeWorkflow)
class TypeWorkflowAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'categorie', 'duree_standard_minutes', 'est_actif']
    list_filter = ['categorie', 'est_actif']
    search_fields = ['nom', 'code', 'description']
    ordering = ['ordre_affichage', 'nom']
    inlines = [EtapeWorkflowInline]


@admin.register(EtapeWorkflow)
class EtapeWorkflowAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_workflow', 'ordre', 'duree_estimee_minutes', 'est_obligatoire']
    list_filter = ['type_workflow', 'est_obligatoire']
    search_fields = ['nom', 'code']
    ordering = ['type_workflow', 'ordre']


class TransitionEtapeInline(admin.TabularInline):
    model = TransitionEtape
    extra = 0
    readonly_fields = ['horodatage', 'etape_source', 'etape_destination', 'effectuee_par']
    ordering = ['horodatage']


@admin.register(InstanceWorkflow)
class InstanceWorkflowAdmin(admin.ModelAdmin):
    list_display = [
        'reference_patient', 'type_workflow', 'statut', 'priorite',
        'etape_actuelle', 'departement', 'demarre_le'
    ]
    list_filter = ['statut', 'priorite', 'type_workflow', 'departement']
    search_fields = ['reference_patient', 'notes']
    readonly_fields = ['demarre_le', 'termine_le', 'modifie_le']
    ordering = ['-demarre_le']
    inlines = [TransitionEtapeInline]


@admin.register(TransitionEtape)
class TransitionEtapeAdmin(admin.ModelAdmin):
    list_display = ['instance', 'etape_source', 'etape_destination', 'effectuee_par', 'horodatage']
    list_filter = ['horodatage']
    search_fields = ['instance__reference_patient', 'commentaire']
    readonly_fields = ['horodatage']
    ordering = ['-horodatage']
