from rest_framework import serializers
from .models import Service, TypeFlux, MicroEvenement, Alerte, Rapport
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class TypeFluxSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeFlux
        fields = '__all__'

class MicroEvenementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicroEvenement
        fields = '__all__'

class AlerteSerializer(serializers.ModelSerializer):
    service_nom = serializers.ReadOnlyField(source='service.nom')
    class Meta:
        model = Alerte
        fields = ['id', 'service', 'service_nom', 'message', 'niveau_gravite', 'genere_le', 'est_resolu']

class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = '__all__'
