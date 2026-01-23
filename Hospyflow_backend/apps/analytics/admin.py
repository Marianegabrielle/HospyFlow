from django.contrib import admin
from .models import AnalyseGoulotEtranglement, MetriqueDepartement, StatistiqueGlobale


@admin.register(AnalyseGoulotEtranglement)
class AnalyseGoulotAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'departement', 'gravite', 'statut',
        'delai_moyen_minutes', 'nombre_occurrences', 'detecte_le'
    ]
    list_filter = ['gravite', 'statut', 'departement', 'type_workflow']
    search_fields = ['titre', 'description', 'recommandations']
    ordering = ['-detecte_le']
    readonly_fields = ['detecte_le', 'confirme_le', 'resolu_le']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'statut', 'gravite')
        }),
        ('Localisation', {
            'fields': ('departement', 'type_workflow', 'etape_concernee')
        }),
        ('Métriques', {
            'fields': ('delai_moyen_minutes', 'nombre_occurrences', 'impact_patients')
        }),
        ('Période d\'analyse', {
            'fields': ('periode_debut', 'periode_fin')
        }),
        ('Recommandations', {
            'fields': ('recommandations',)
        }),
        ('Suivi', {
            'fields': ('detecte_le', 'confirme_le', 'confirme_par', 'resolu_le')
        }),
    )


@admin.register(MetriqueDepartement)
class MetriqueDepartementAdmin(admin.ModelAdmin):
    list_display = [
        'departement', 'date',
        'workflows_demarre', 'workflows_termines',
        'evenements_signales', 'evenements_critiques',
        'score_efficacite'
    ]
    list_filter = ['departement', 'date']
    ordering = ['-date', 'departement']


@admin.register(StatistiqueGlobale)
class StatistiqueGlobaleAdmin(admin.ModelAdmin):
    list_display = [
        'date',
        'total_workflows_actifs', 'total_workflows_termines',
        'total_evenements_ouverts', 'total_evenements_critiques',
        'total_goulots_actifs', 'score_global_efficacite'
    ]
    list_filter = ['date']
    ordering = ['-date']
