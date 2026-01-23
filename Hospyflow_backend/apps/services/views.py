"""
Views pour l'API Services.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.translation import gettext_lazy as _

from .models import ServiceHospitalier
from .serializers import ServiceHospitalierSerializer, ServiceSummarySerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les services hospitaliers.
    Compatible avec l'ancien backend ops/.
    """
    queryset = ServiceHospitalier.objects.select_related('department').all()
    serializer_class = ServiceHospitalierSerializer
    
    # Temporairement sans authentification pour faciliter la migration
    permission_classes = [AllowAny]
    
    def list(self, request, *args, **kwargs):
        """
        Liste tous les services hospitaliers.
        GET /api/services/
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retourne un résumé de tous les services avec KPIs.
        GET /api/services/summary/
        
        Compatible avec l'ancien endpoint du backend ops/.
        """
        # Utiliser un objet vide car le serializer calcule tout dynamiquement
        serializer = ServiceSummarySerializer({})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def recalculer_saturation(self, request, pk=None):
        """
        Recalcule la saturation d'un service.
        POST /api/services/{id}/recalculer_saturation/
        """
        service = self.get_object()
        saturation = service.calculer_saturation()
        
        return Response({
            'message': _('Saturation recalculée'),
            'saturation': saturation,
            'etat': service.etat
        })
