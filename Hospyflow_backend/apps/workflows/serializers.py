from rest_framework import serializers

from .models import TypeWorkflow, EtapeWorkflow, InstanceWorkflow, TransitionEtape


class EtapeWorkflowSerializer(serializers.ModelSerializer):
    """Serializer pour les étapes de workflow."""
    
    departement_nom = serializers.CharField(
        source='departement_responsable.name',
        read_only=True
    )
    
    class Meta:
        model = EtapeWorkflow
        fields = [
            'id', 'nom', 'code', 'description', 'ordre',
            'duree_estimee_minutes', 'est_obligatoire',
            'departement_responsable', 'departement_nom'
        ]
        read_only_fields = ['id']


class TypeWorkflowSerializer(serializers.ModelSerializer):
    """Serializer pour les types de workflow."""
    
    categorie_display = serializers.CharField(
        source='get_categorie_display',
        read_only=True
    )
    nombre_etapes = serializers.SerializerMethodField()
    
    class Meta:
        model = TypeWorkflow
        fields = [
            'id', 'nom', 'code', 'categorie', 'categorie_display',
            'description', 'duree_standard_minutes', 'seuil_alerte_minutes',
            'est_actif', 'ordre_affichage', 'nombre_etapes'
        ]
        read_only_fields = ['id', 'cree_le', 'modifie_le']
    
    def get_nombre_etapes(self, obj):
        return obj.etapes.count()


class TypeWorkflowDetailSerializer(TypeWorkflowSerializer):
    """Serializer détaillé avec les étapes incluses."""
    
    etapes = EtapeWorkflowSerializer(many=True, read_only=True)
    
    class Meta(TypeWorkflowSerializer.Meta):
        fields = TypeWorkflowSerializer.Meta.fields + ['etapes']


class TransitionEtapeSerializer(serializers.ModelSerializer):
    """Serializer pour les transitions d'étapes."""
    
    etape_source_nom = serializers.CharField(
        source='etape_source.nom',
        read_only=True,
        allow_null=True
    )
    etape_destination_nom = serializers.CharField(
        source='etape_destination.nom',
        read_only=True,
        allow_null=True
    )
    effectuee_par_nom = serializers.CharField(
        source='effectuee_par.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = TransitionEtape
        fields = [
            'id', 'etape_source', 'etape_source_nom',
            'etape_destination', 'etape_destination_nom',
            'effectuee_par', 'effectuee_par_nom',
            'horodatage', 'duree_etape_minutes', 'commentaire'
        ]
        read_only_fields = ['id', 'horodatage']


class InstanceWorkflowSerializer(serializers.ModelSerializer):
    """Serializer pour les instances de workflow."""
    
    type_workflow_nom = serializers.CharField(
        source='type_workflow.nom',
        read_only=True
    )
    etape_actuelle_nom = serializers.CharField(
        source='etape_actuelle.nom',
        read_only=True,
        allow_null=True
    )
    departement_nom = serializers.CharField(
        source='departement.name',
        read_only=True
    )
    initie_par_nom = serializers.CharField(
        source='initie_par.get_full_name',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    priorite_display = serializers.CharField(
        source='get_priorite_display',
        read_only=True
    )
    est_en_retard = serializers.BooleanField(read_only=True)
    duree_ecoulee_minutes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = InstanceWorkflow
        fields = [
            'id', 'type_workflow', 'type_workflow_nom',
            'reference_patient', 'etape_actuelle', 'etape_actuelle_nom',
            'statut', 'statut_display', 'priorite', 'priorite_display',
            'departement', 'departement_nom',
            'initie_par', 'initie_par_nom',
            'notes', 'demarre_le', 'termine_le', 'modifie_le',
            'est_en_retard', 'duree_ecoulee_minutes'
        ]
        read_only_fields = [
            'id', 'initie_par', 'demarre_le', 'termine_le', 'modifie_le'
        ]


class InstanceWorkflowDetailSerializer(InstanceWorkflowSerializer):
    """Serializer détaillé avec l'historique des transitions."""
    
    transitions = TransitionEtapeSerializer(many=True, read_only=True)
    type_workflow_detail = TypeWorkflowDetailSerializer(
        source='type_workflow',
        read_only=True
    )
    
    class Meta(InstanceWorkflowSerializer.Meta):
        fields = InstanceWorkflowSerializer.Meta.fields + [
            'transitions', 'type_workflow_detail'
        ]


class DemarrerWorkflowSerializer(serializers.Serializer):
    """Serializer pour démarrer un nouveau workflow."""
    
    type_workflow = serializers.IntegerField(
        help_text="ID du type de workflow"
    )
    reference_patient = serializers.CharField(
        max_length=50,
        help_text="Référence anonymisée du patient"
    )
    departement = serializers.IntegerField(
        help_text="ID du département"
    )
    priorite = serializers.ChoiceField(
        choices=InstanceWorkflow.Priorite.choices,
        default='NORMALE'
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default=''
    )


class AvancerEtapeSerializer(serializers.Serializer):
    """Serializer pour faire avancer une étape."""
    
    commentaire = serializers.CharField(
        required=False,
        allow_blank=True,
        default=''
    )


class AbandonnerWorkflowSerializer(serializers.Serializer):
    """Serializer pour abandonner un workflow."""
    
    raison = serializers.CharField(
        required=True,
        help_text="Raison de l'abandon du workflow"
    )
