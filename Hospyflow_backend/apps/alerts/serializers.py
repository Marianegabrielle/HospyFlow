from rest_framework import serializers
from .models import Alerte, RegleAlerte, AbonnementAlerte


class RegleAlerteSerializer(serializers.ModelSerializer):
    """Serializer pour les règles d'alerte."""
    
    type_regle_display = serializers.CharField(
        source='get_type_regle_display',
        read_only=True
    )
    priorite_display = serializers.CharField(
        source='get_priorite_display',
        read_only=True
    )
    departement_nom = serializers.CharField(
        source='departement.name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = RegleAlerte
        fields = [
            'id', 'nom', 'code', 'description',
            'type_regle', 'type_regle_display',
            'seuil_valeur', 'periode_minutes',
            'departement', 'departement_nom', 'type_workflow',
            'priorite', 'priorite_display',
            'message_template', 'est_actif',
            'cree_le', 'modifie_le', 'cree_par'
        ]
        read_only_fields = ['id', 'cree_le', 'modifie_le', 'cree_par']


class AlerteSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes."""
    
    priorite_display = serializers.CharField(
        source='get_priorite_display',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    departement_nom = serializers.CharField(
        source='departement.name',
        read_only=True,
        allow_null=True
    )
    regle_nom = serializers.CharField(
        source='regle.nom',
        read_only=True,
        allow_null=True
    )
    acquittee_par_nom = serializers.CharField(
        source='acquittee_par.get_full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Alerte
        fields = [
            'id', 'titre', 'message',
            'priorite', 'priorite_display',
            'statut', 'statut_display',
            'departement', 'departement_nom',
            'regle', 'regle_nom',
            'evenement', 'goulot', 'workflow',
            'donnees_contexte',
            'cree_le', 'vue_le', 'acquittee_le', 'resolue_le',
            'acquittee_par', 'acquittee_par_nom'
        ]
        read_only_fields = [
            'id', 'cree_le', 'vue_le', 'acquittee_le',
            'resolue_le', 'acquittee_par'
        ]


class AbonnementAlerteSerializer(serializers.ModelSerializer):
    """Serializer pour les abonnements aux alertes."""
    
    priorite_minimum_display = serializers.CharField(
        source='get_priorite_minimum_display',
        read_only=True
    )
    canal_display = serializers.CharField(
        source='get_canal_display',
        read_only=True
    )
    
    class Meta:
        model = AbonnementAlerte
        fields = [
            'id', 'utilisateur',
            'priorite_minimum', 'priorite_minimum_display',
            'departements', 'types_regles',
            'canal', 'canal_display',
            'est_actif', 'cree_le', 'modifie_le'
        ]
        read_only_fields = ['id', 'utilisateur', 'cree_le', 'modifie_le']


class CreerAbonnementSerializer(serializers.Serializer):
    """Serializer pour créer un abonnement."""
    
    priorite_minimum = serializers.ChoiceField(
        choices=Alerte.Priorite.choices,
        default='NORMALE'
    )
    departements = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
    canal = serializers.ChoiceField(
        choices=AbonnementAlerte.CanalNotification.choices,
        default='APP'
    )
