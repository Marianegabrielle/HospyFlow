from rest_framework import serializers
from django.utils import timezone

from .models import (
    CategorieEvenement,
    MicroEvenement,
    PieceJointeEvenement,
    CommentaireEvenement
)


class CategorieEvenementSerializer(serializers.ModelSerializer):
    """Serializer pour les catégories d'événements."""
    
    type_display = serializers.CharField(
        source='get_type_categorie_display',
        read_only=True
    )
    
    class Meta:
        model = CategorieEvenement
        fields = [
            'id', 'nom', 'code', 'type_categorie', 'type_display',
            'description', 'icone', 'couleur', 'ordre_affichage'
        ]
        read_only_fields = ['id']


class PieceJointeSerializer(serializers.ModelSerializer):
    """Serializer pour les pièces jointes."""
    
    class Meta:
        model = PieceJointeEvenement
        fields = ['id', 'fichier', 'type_fichier', 'nom_original', 'ajoute_le']
        read_only_fields = ['id', 'ajoute_le']


class CommentaireEvenementSerializer(serializers.ModelSerializer):
    """Serializer pour les commentaires."""
    
    auteur_nom = serializers.CharField(
        source='auteur.get_full_name',
        read_only=True
    )
    auteur_role = serializers.CharField(
        source='auteur.get_role_display',
        read_only=True
    )
    
    class Meta:
        model = CommentaireEvenement
        fields = ['id', 'auteur', 'auteur_nom', 'auteur_role', 'contenu', 'cree_le']
        read_only_fields = ['id', 'auteur', 'cree_le']


class MicroEvenementSerializer(serializers.ModelSerializer):
    """Serializer pour les micro-événements."""
    
    rapporteur_nom = serializers.CharField(
        source='rapporteur.get_full_name',
        read_only=True
    )
    rapporteur_role = serializers.CharField(
        source='rapporteur.get_role_display',
        read_only=True
    )
    departement_nom = serializers.CharField(
        source='departement.name',
        read_only=True
    )
    categorie_nom = serializers.CharField(
        source='categorie.nom',
        read_only=True
    )
    severite_display = serializers.CharField(
        source='get_severite_display',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    est_resolu = serializers.BooleanField(read_only=True)
    duree_resolution_minutes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = MicroEvenement
        fields = [
            'id', 'rapporteur', 'rapporteur_nom', 'rapporteur_role',
            'departement', 'departement_nom',
            'instance_workflow',
            'categorie', 'categorie_nom',
            'titre', 'description',
            'severite', 'severite_display',
            'statut', 'statut_display',
            'delai_estime_minutes', 'lieu',
            'survenu_le', 'signale_le', 'resolu_le', 'modifie_le',
            'resolu_par', 'commentaire_resolution',
            'est_recurrent', 'est_resolu', 'duree_resolution_minutes'
        ]
        read_only_fields = [
            'id', 'rapporteur', 'signale_le', 'resolu_le',
            'modifie_le', 'resolu_par'
        ]


class MicroEvenementDetailSerializer(MicroEvenementSerializer):
    """Serializer détaillé avec commentaires et pièces jointes."""
    
    commentaires = CommentaireEvenementSerializer(many=True, read_only=True)
    pieces_jointes = PieceJointeSerializer(many=True, read_only=True)
    
    class Meta(MicroEvenementSerializer.Meta):
        fields = MicroEvenementSerializer.Meta.fields + [
            'commentaires', 'pieces_jointes'
        ]


class SignalerEvenementSerializer(serializers.Serializer):
    """Serializer pour signaler un nouvel événement."""
    
    titre = serializers.CharField(
        max_length=200,
        help_text="Titre court décrivant l'événement"
    )
    description = serializers.CharField(
        help_text="Description détaillée de l'événement"
    )
    departement = serializers.IntegerField(
        help_text="ID du département concerné"
    )
    categorie = serializers.IntegerField(
        help_text="ID de la catégorie d'événement"
    )
    severite = serializers.ChoiceField(
        choices=MicroEvenement.Severite.choices,
        default='MOYEN'
    )
    survenu_le = serializers.DateTimeField(
        required=False,
        default=None,
        help_text="Date/heure de survenue (défaut: maintenant)"
    )
    delai_estime_minutes = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        help_text="Impact estimé en minutes"
    )
    lieu = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        help_text="Emplacement précis"
    )
    instance_workflow = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID de l'instance de workflow associée"
    )
    
    def validate_survenu_le(self, value):
        if value and value > timezone.now():
            raise serializers.ValidationError(
                "La date de survenue ne peut pas être dans le futur."
            )
        return value


class ResoudreEvenementSerializer(serializers.Serializer):
    """Serializer pour résoudre un événement."""
    
    commentaire_resolution = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Commentaire expliquant la résolution"
    )


class AjouterCommentaireSerializer(serializers.Serializer):
    """Serializer pour ajouter un commentaire."""
    
    contenu = serializers.CharField(
        help_text="Contenu du commentaire"
    )
