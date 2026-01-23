from rest_framework import serializers
from .models import AnalyseGoulotEtranglement, MetriqueDepartement, StatistiqueGlobale, Rapport


class AnalyseGoulotSerializer(serializers.ModelSerializer):
    """Serializer pour les analyses de goulots."""
    
    departement_nom = serializers.CharField(
        source='departement.name',
        read_only=True
    )
    type_workflow_nom = serializers.CharField(
        source='type_workflow.nom',
        read_only=True,
        allow_null=True
    )
    etape_nom = serializers.CharField(
        source='etape_concernee.nom',
        read_only=True,
        allow_null=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    gravite_display = serializers.CharField(
        source='get_gravite_display',
        read_only=True
    )
    
    class Meta:
        model = AnalyseGoulotEtranglement
        fields = [
            'id', 'departement', 'departement_nom',
            'type_workflow', 'type_workflow_nom',
            'etape_concernee', 'etape_nom',
            'titre', 'description',
            'statut', 'statut_display',
            'gravite', 'gravite_display',
            'delai_moyen_minutes', 'nombre_occurrences', 'impact_patients',
            'periode_debut', 'periode_fin',
            'recommandations',
            'detecte_le', 'confirme_le', 'resolu_le', 'confirme_par'
        ]
        read_only_fields = ['id', 'detecte_le']


class MetriqueDepartementSerializer(serializers.ModelSerializer):
    """Serializer pour les métriques de département."""
    
    departement_nom = serializers.CharField(
        source='departement.name',
        read_only=True
    )
    
    class Meta:
        model = MetriqueDepartement
        fields = [
            'id', 'departement', 'departement_nom', 'date',
            'workflows_demarre', 'workflows_termines', 'workflows_abandonnes',
            'duree_moyenne_workflow_minutes',
            'evenements_signales', 'evenements_resolus', 'evenements_critiques',
            'delai_resolution_moyen_minutes',
            'personnel_en_service', 'score_efficacite'
        ]


class StatistiqueGlobaleSerializer(serializers.ModelSerializer):
    """Serializer pour les statistiques globales."""
    
    class Meta:
        model = StatistiqueGlobale
        fields = [
            'id', 'date',
            'total_workflows_actifs', 'total_workflows_termines',
            'total_evenements_ouverts', 'total_evenements_critiques',
            'total_goulots_actifs',
            'temps_attente_moyen_minutes', 'temps_resolution_moyen_minutes',
            'score_global_efficacite', 'personnel_total_en_service'
        ]


class ConfirmerGoulotSerializer(serializers.Serializer):
    """Serializer pour confirmer un goulot."""
    
    recommandations = serializers.CharField(
        required=False,
        allow_blank=True
    )


class ResoudreGoulotSerializer(serializers.Serializer):
    """Serializer pour résoudre un goulot."""
    
    commentaire = serializers.CharField(
        required=False,
        allow_blank=True
    )


class RapportSerializer(serializers.ModelSerializer):
    """
    Serializer pour les rapports.
    Compatible avec l'ancien backend ops/.
    """
    
    format_display = serializers.CharField(
        source='get_format_display',
        read_only=True
    )
    
    genere_par_nom = serializers.SerializerMethodField()
    
    class Meta:
        model = Rapport
        fields = [
            'id', 'plage_date', 'donnees_metriques',
            'format', 'format_display',
            'fichier', 'genere_le', 'genere_par', 'genere_par_nom'
        ]
        read_only_fields = ['id', 'genere_le', 'genere_par']
    
    def get_genere_par_nom(self, obj):
        """Retourne le nom complet de l'utilisateur qui a généré le rapport."""
        if obj.genere_par:
            return obj.genere_par.get_full_name()
        return None
