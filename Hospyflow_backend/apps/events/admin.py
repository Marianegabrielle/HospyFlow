from django.contrib import admin
from .models import (
    CategorieEvenement,
    MicroEvenement,
    PieceJointeEvenement,
    CommentaireEvenement
)


@admin.register(CategorieEvenement)
class CategorieEvenementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'type_categorie', 'couleur', 'est_actif']
    list_filter = ['type_categorie', 'est_actif']
    search_fields = ['nom', 'code', 'description']
    ordering = ['ordre_affichage', 'nom']


class PieceJointeInline(admin.TabularInline):
    model = PieceJointeEvenement
    extra = 0


class CommentaireInline(admin.TabularInline):
    model = CommentaireEvenement
    extra = 0
    readonly_fields = ['auteur', 'cree_le']


@admin.register(MicroEvenement)
class MicroEvenementAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'severite', 'statut', 'departement',
        'rapporteur', 'signale_le', 'est_recurrent'
    ]
    list_filter = ['severite', 'statut', 'categorie', 'departement', 'est_recurrent']
    search_fields = ['titre', 'description', 'lieu']
    readonly_fields = ['signale_le', 'resolu_le', 'modifie_le']
    ordering = ['-signale_le']
    inlines = [PieceJointeInline, CommentaireInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'categorie', 'lieu')
        }),
        ('Classification', {
            'fields': ('severite', 'statut', 'est_recurrent')
        }),
        ('Contexte', {
            'fields': ('departement', 'instance_workflow', 'delai_estime_minutes')
        }),
        ('Signalement', {
            'fields': ('rapporteur', 'survenu_le', 'signale_le')
        }),
        ('Résolution', {
            'fields': ('resolu_par', 'resolu_le', 'commentaire_resolution'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommentaireEvenement)
class CommentaireEvenementAdmin(admin.ModelAdmin):
    list_display = ['evenement', 'auteur', 'cree_le']
    list_filter = ['cree_le']
    search_fields = ['contenu', 'evenement__titre']
    readonly_fields = ['cree_le']
