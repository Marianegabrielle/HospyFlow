from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import MicroEvenement, CategorieEvenement
from .serializers import (
    CategorieEvenementSerializer,
    MicroEvenementSerializer,
    MicroEvenementDetailSerializer,
    CommentaireEvenementSerializer,
    SignalerEvenementSerializer,
    ResoudreEvenementSerializer,
    AjouterCommentaireSerializer
)
from .services import GestionEvenementService, EvenementException
from .repositories import MicroEvenementRepository, CategorieEvenementRepository
from apps.accounts.permissions import IsAdminUser, IsMedicalStaff


class CategorieEvenementListView(generics.ListAPIView):
    """Liste toutes les catégories d'événements actives."""
    serializer_class = CategorieEvenementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CategorieEvenementRepository.obtenir_toutes_actives()


class MicroEvenementListView(generics.ListAPIView):
    """Liste les micro-événements avec filtres."""
    serializer_class = MicroEvenementSerializer
    permission_classes = [permissions.AllowAny] # Temporaire pour migration
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['departement', 'categorie', 'severite', 'statut', 'est_recurrent']
    search_fields = ['titre', 'description', 'lieu']
    ordering_fields = ['signale_le', 'severite', 'statut']
    ordering = ['-signale_le']
    
    def get_queryset(self):
        queryset = MicroEvenement.objects.select_related(
            'rapporteur', 'departement', 'categorie'
        )
        
        # Filtrer par département de l'utilisateur si c'est du personnel médical
        utilisateur = self.request.user
        if utilisateur.is_medical_staff and utilisateur.department:
            queryset = queryset.filter(departement=utilisateur.department)
        
        return queryset


class MicroEvenementDetailView(generics.RetrieveAPIView):
    """Détails d'un micro-événement avec commentaires."""
    queryset = MicroEvenement.objects.all()
    serializer_class = MicroEvenementDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class MesEvenementsView(generics.ListAPIView):
    """Liste les événements signalés par l'utilisateur connecté."""
    serializer_class = MicroEvenementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MicroEvenementRepository.obtenir_par_rapporteur(
            self.request.user.id
        )


class EvenementsCritiquesView(generics.ListAPIView):
    """Liste les événements critiques non résolus."""
    serializer_class = MicroEvenementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MicroEvenementRepository.obtenir_critiques()


class EvenementsRecentsView(generics.ListAPIView):
    """Liste les événements des dernières 24 heures."""
    serializer_class = MicroEvenementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        heures = int(self.request.query_params.get('heures', 24))
        return MicroEvenementRepository.obtenir_recents(heures=heures)


class SignalerEvenementView(APIView):
    """Endpoint pour signaler un nouveau micro-événement."""
    permission_classes = [permissions.IsAuthenticated, IsMedicalStaff]
    
    def post(self, request):
        serializer = SignalerEvenementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = GestionEvenementService()
        
        try:
            evenement = service.signaler_evenement(
                rapporteur=request.user,
                titre=serializer.validated_data['titre'],
                description=serializer.validated_data['description'],
                departement_id=serializer.validated_data['departement'],
                categorie_id=serializer.validated_data['categorie'],
                severite=serializer.validated_data.get('severite', 'MOYEN'),
                survenu_le=serializer.validated_data.get('survenu_le'),
                delai_estime_minutes=serializer.validated_data.get('delai_estime_minutes'),
                lieu=serializer.validated_data.get('lieu', ''),
                instance_workflow_id=serializer.validated_data.get('instance_workflow')
            )
            
            return Response({
                'message': 'Événement signalé avec succès.',
                'evenement': MicroEvenementSerializer(evenement).data
            }, status=status.HTTP_201_CREATED)
            
        except EvenementException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PrendreEnChargeView(APIView):
    """Endpoint pour prendre en charge un événement."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        service = GestionEvenementService()
        
        try:
            evenement = service.prendre_en_charge(
                evenement_id=pk,
                utilisateur=request.user
            )
            
            return Response({
                'message': 'Événement pris en charge.',
                'evenement': MicroEvenementSerializer(evenement).data
            })
            
        except EvenementException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ResoudreEvenementView(APIView):
    """Endpoint pour résoudre un événement."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        serializer = ResoudreEvenementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = GestionEvenementService()
        
        try:
            evenement = service.resoudre_evenement(
                evenement_id=pk,
                resolu_par=request.user,
                commentaire_resolution=serializer.validated_data.get(
                    'commentaire_resolution', ''
                )
            )
            
            return Response({
                'message': 'Événement résolu.',
                'evenement': MicroEvenementSerializer(evenement).data
            })
            
        except EvenementException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AjouterCommentaireView(APIView):
    """Endpoint pour ajouter un commentaire à un événement."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        serializer = AjouterCommentaireSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = GestionEvenementService()
        
        try:
            commentaire = service.ajouter_commentaire(
                evenement_id=pk,
                auteur=request.user,
                contenu=serializer.validated_data['contenu']
            )
            
            return Response({
                'message': 'Commentaire ajouté.',
                'commentaire': CommentaireEvenementSerializer(commentaire).data
            }, status=status.HTTP_201_CREATED)
            
        except EvenementException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class MarquerRecurrentView(APIView):
    """Endpoint pour marquer un événement comme récurrent."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request, pk):
        service = GestionEvenementService()
        
        try:
            evenement = service.marquer_recurrent(pk)
            
            return Response({
                'message': 'Événement marqué comme récurrent.',
                'evenement': MicroEvenementSerializer(evenement).data
            })
            
        except EvenementException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class StatistiquesEvenementsView(APIView):
    """Endpoint pour les statistiques d'événements par département."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        departement_id = request.query_params.get('departement')
        
        if not departement_id:
            # Si pas de département spécifié, utiliser celui de l'utilisateur
            if request.user.department:
                departement_id = request.user.department.id
            else:
                return Response({
                    'erreur': 'Veuillez spécifier un département.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        service = GestionEvenementService()
        stats = service.obtenir_statistiques_departement(int(departement_id))
        
        return Response(stats)


class TendancesEvenementsView(APIView):
    """Endpoint pour les tendances d'événements."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        jours = int(request.query_params.get('jours', 7))
        
        service = GestionEvenementService()
        tendances = service.obtenir_tendances(jours=jours)
        
        return Response({
            'periode_jours': jours,
            'tendances': tendances
        })
