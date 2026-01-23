from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from .models import Alerte, RegleAlerte, AbonnementAlerte
from .serializers import (
    AlerteSerializer,
    RegleAlerteSerializer,
    AbonnementAlerteSerializer,
    CreerAbonnementSerializer
)
from .services import GestionAlerteService, MoteurReglesService, AlerteException
from apps.accounts.permissions import IsAdminUser


class AlerteListView(generics.ListAPIView):
    """Liste les alertes."""
    serializer_class = AlerteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['statut', 'priorite', 'departement']
    ordering = ['-cree_le']
    
    def get_queryset(self):
        service = GestionAlerteService()
        non_lues = self.request.query_params.get('non_lues', 'false').lower() == 'true'
        return service.obtenir_alertes_utilisateur(
            self.request.user,
            non_lues_seulement=non_lues
        )


class AlerteDetailView(generics.RetrieveAPIView):
    """Détails d'une alerte."""
    queryset = Alerte.objects.all()
    serializer_class = AlerteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        
        # Marquer comme vue
        service = GestionAlerteService()
        service.marquer_vue(kwargs['pk'])
        
        return response


class MesAlertesView(APIView):
    """Alertes non lues de l'utilisateur connecté."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        service = GestionAlerteService()
        alertes = service.obtenir_alertes_utilisateur(
            request.user,
            non_lues_seulement=True
        )
        
        return Response({
            'nombre': len(alertes),
            'alertes': AlerteSerializer(alertes, many=True).data
        })


class AcquitterAlerteView(APIView):
    """Acquitte une alerte."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        service = GestionAlerteService()
        
        try:
            alerte = service.acquitter(pk, request.user)
            return Response({
                'message': 'Alerte acquittée.',
                'alerte': AlerteSerializer(alerte).data
            })
        except AlerteException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ResoudreAlerteView(APIView):
    """Résout une alerte."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        service = GestionAlerteService()
        
        try:
            alerte = service.resoudre(pk)
            return Response({
                'message': 'Alerte résolue.',
                'alerte': AlerteSerializer(alerte).data
            })
        except AlerteException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class IgnorerAlerteView(APIView):
    """Ignore une alerte."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        service = GestionAlerteService()
        
        try:
            alerte = service.ignorer(pk)
            return Response({
                'message': 'Alerte ignorée.',
                'alerte': AlerteSerializer(alerte).data
            })
        except AlerteException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RegleAlerteListCreateView(generics.ListCreateAPIView):
    """Liste et crée des règles d'alerte."""
    queryset = RegleAlerte.objects.all()
    serializer_class = RegleAlerteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filterset_fields = ['type_regle', 'est_actif', 'departement']
    
    def perform_create(self, serializer):
        serializer.save(cree_par=self.request.user)


class RegleAlerteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détails, modification et suppression de règle."""
    queryset = RegleAlerte.objects.all()
    serializer_class = RegleAlerteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class EvaluerReglesView(APIView):
    """Évalue manuellement toutes les règles (admin)."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        service = MoteurReglesService()
        alertes = service.evaluer_toutes_regles()
        
        return Response({
            'message': f'{len(alertes)} alerte(s) générée(s).',
            'alertes': AlerteSerializer(alertes, many=True).data
        })


class MesAbonnementsView(generics.ListAPIView):
    """Liste les abonnements de l'utilisateur."""
    serializer_class = AbonnementAlerteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AbonnementAlerte.objects.filter(
            utilisateur=self.request.user
        )


class CreerAbonnementView(APIView):
    """Crée ou met à jour un abonnement."""
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        serializer = CreerAbonnementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        canal = serializer.validated_data['canal']
        
        abonnement, created = AbonnementAlerte.objects.update_or_create(
            utilisateur=request.user,
            canal=canal,
            defaults={
                'priorite_minimum': serializer.validated_data['priorite_minimum'],
                'est_actif': True
            }
        )
        
        # Gérer les départements
        departements = serializer.validated_data.get('departements', [])
        if departements:
            abonnement.departements.set(departements)
        
        message = 'Abonnement créé.' if created else 'Abonnement mis à jour.'
        
        return Response({
            'message': message,
            'abonnement': AbonnementAlerteSerializer(abonnement).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SupprimerAbonnementView(APIView):
    """Supprime un abonnement."""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        try:
            abonnement = AbonnementAlerte.objects.get(
                pk=pk,
                utilisateur=request.user
            )
            abonnement.delete()
            return Response({
                'message': 'Abonnement supprimé.'
            }, status=status.HTTP_204_NO_CONTENT)
        except AbonnementAlerte.DoesNotExist:
            return Response({
                'erreur': 'Abonnement introuvable.'
            }, status=status.HTTP_404_NOT_FOUND)
