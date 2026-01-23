from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import AnalyseGoulotEtranglement, MetriqueDepartement, StatistiqueGlobale, Rapport
from .serializers import (
    AnalyseGoulotSerializer,
    MetriqueDepartementSerializer,
    StatistiqueGlobaleSerializer,
    ConfirmerGoulotSerializer,
    ResoudreGoulotSerializer,
    RapportSerializer
)
from .services import MoteurAnalyseService, TableauBordService
from apps.accounts.permissions import IsAdminUser


class TableauBordView(APIView):
    """Endpoint principal du tableau de bord analytique."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        service = TableauBordService()
        donnees = service.obtenir_donnees_tableau_bord()
        return Response(donnees)


class GoulotListView(generics.ListAPIView):
    """Liste les goulots d'étranglement."""
    serializer_class = AnalyseGoulotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['departement', 'type_workflow', 'statut', 'gravite']
    ordering = ['-detecte_le']
    
    def get_queryset(self):
        queryset = AnalyseGoulotEtranglement.objects.select_related(
            'departement', 'type_workflow', 'etape_concernee'
        )
        
        # Par défaut, afficher les goulots actifs
        statut = self.request.query_params.get('statut')
        if not statut:
            queryset = queryset.filter(
                statut__in=['DETECTE', 'EN_ANALYSE', 'CONFIRME']
            )
        
        return queryset


class GoulotDetailView(generics.RetrieveAPIView):
    """Détails d'un goulot d'étranglement."""
    queryset = AnalyseGoulotEtranglement.objects.all()
    serializer_class = AnalyseGoulotSerializer
    permission_classes = [permissions.IsAuthenticated]


class DetecterGoulotsView(APIView):
    """Endpoint pour lancer une détection de goulots."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        departement_id = request.data.get('departement')
        jours = int(request.data.get('jours', 7))
        
        service = MoteurAnalyseService()
        goulots = service.detecter_goulots_etranglement(
            departement_id=departement_id,
            jours=jours
        )
        
        return Response({
            'message': f'{len(goulots)} goulot(s) détecté(s).',
            'goulots': AnalyseGoulotSerializer(goulots, many=True).data
        }, status=status.HTTP_201_CREATED)


class ConfirmerGoulotView(APIView):
    """Confirme un goulot détecté."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request, pk):
        serializer = ConfirmerGoulotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            goulot = AnalyseGoulotEtranglement.objects.get(pk=pk)
        except AnalyseGoulotEtranglement.DoesNotExist:
            return Response({
                'erreur': 'Goulot introuvable.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        goulot.statut = 'CONFIRME'
        goulot.confirme_le = timezone.now()
        goulot.confirme_par = request.user
        
        if serializer.validated_data.get('recommandations'):
            goulot.recommandations = serializer.validated_data['recommandations']
        
        goulot.save()
        
        return Response({
            'message': 'Goulot confirmé.',
            'goulot': AnalyseGoulotSerializer(goulot).data
        })


class ResoudreGoulotView(APIView):
    """Marque un goulot comme résolu."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request, pk):
        try:
            goulot = AnalyseGoulotEtranglement.objects.get(pk=pk)
        except AnalyseGoulotEtranglement.DoesNotExist:
            return Response({
                'erreur': 'Goulot introuvable.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        goulot.statut = 'RESOLU'
        goulot.resolu_le = timezone.now()
        goulot.save()
        
        return Response({
            'message': 'Goulot résolu.',
            'goulot': AnalyseGoulotSerializer(goulot).data
        })


class MarquerFauxPositifView(APIView):
    """Marque un goulot comme faux positif."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request, pk):
        try:
            goulot = AnalyseGoulotEtranglement.objects.get(pk=pk)
        except AnalyseGoulotEtranglement.DoesNotExist:
            return Response({
                'erreur': 'Goulot introuvable.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        goulot.statut = 'FAUX_POSITIF'
        goulot.save()
        
        return Response({
            'message': 'Goulot marqué comme faux positif.',
            'goulot': AnalyseGoulotSerializer(goulot).data
        })


class MetriquesDepartementView(generics.ListAPIView):
    """Métriques par département."""
    serializer_class = MetriqueDepartementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['departement', 'date']
    ordering = ['-date']
    
    def get_queryset(self):
        return MetriqueDepartement.objects.select_related('departement')


class MetriquesDepartementDetailView(APIView):
    """Métriques détaillées pour un département spécifique."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, departement_id):
        jours = int(request.query_params.get('jours', 30))
        
        metriques = MetriqueDepartement.objects.filter(
            departement_id=departement_id
        ).order_by('-date')[:jours]
        
        return Response({
            'departement_id': departement_id,
            'periode_jours': jours,
            'metriques': MetriqueDepartementSerializer(metriques, many=True).data
        })


class StatistiquesGlobalesView(generics.ListAPIView):
    """Statistiques globales historiques."""
    serializer_class = StatistiqueGlobaleSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-date']
    
    def get_queryset(self):
        jours = int(self.request.query_params.get('jours', 30))
        return StatistiqueGlobale.objects.all()[:jours]


class GenererStatistiquesView(APIView):
    """Génère les statistiques quotidiennes (admin)."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        service = TableauBordService()
        service.generer_statistiques_quotidiennes()
        
        return Response({
            'message': 'Statistiques quotidiennes générées avec succès.'
        })


class RapportViewSet(generics.ListCreateAPIView):
    """
    ViewSet pour les rapports.
    Compatible avec l'ancien backend ops/.
    
    GET /api/rapports/ - Liste des rapports
    POST /api/rapports/ - Générer un nouveau rapport
    """
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
    permission_classes = [permissions.AllowAny]  # Temporairement sans auth
    ordering = ['-genere_le']
    
    def perform_create(self, serializer):
        """
        Génère un rapport avec les données fournies.
        Compatible avec l'ancien format de l'API ops/.
        """
        # Sauvegarder le rapport
        rapport = serializer.save(genere_par=self.request.user if self.request.user.is_authenticated else None)
        
        # TODO: Implémenter la génération réelle du fichier PDF/CSV
        # Pour l'instant, on sauvegarde juste les métadonnées
        # Dans une version future, on peut utiliser reportlab pour PDF
        # ou csv module pour CSV
        
        return rapport
