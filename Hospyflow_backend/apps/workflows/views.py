from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TypeWorkflow, EtapeWorkflow, InstanceWorkflow
from .serializers import (
    TypeWorkflowSerializer,
    TypeWorkflowDetailSerializer,
    EtapeWorkflowSerializer,
    InstanceWorkflowSerializer,
    InstanceWorkflowDetailSerializer,
    TransitionEtapeSerializer,
    DemarrerWorkflowSerializer,
    AvancerEtapeSerializer,
    AbandonnerWorkflowSerializer
)
from .services import GestionWorkflowService, WorkflowException
from .repositories import TypeWorkflowRepository, InstanceWorkflowRepository
from apps.accounts.permissions import IsAdminUser, IsMedicalStaff


class TypeWorkflowListView(generics.ListAPIView):
    """Liste tous les types de workflows actifs."""
    serializer_class = TypeWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['categorie', 'est_actif']
    search_fields = ['nom', 'code', 'description']
    
    def get_queryset(self):
        return TypeWorkflowRepository.obtenir_tous_actifs()


class TypeWorkflowDetailView(generics.RetrieveAPIView):
    """Détails d'un type de workflow avec ses étapes."""
    queryset = TypeWorkflow.objects.filter(est_actif=True)
    serializer_class = TypeWorkflowDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class TypeWorkflowCreateUpdateView(generics.CreateAPIView, generics.UpdateAPIView):
    """Création et modification de types de workflows (admin seulement)."""
    queryset = TypeWorkflow.objects.all()
    serializer_class = TypeWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class EtapeWorkflowListView(generics.ListAPIView):
    """Liste les étapes d'un type de workflow."""
    serializer_class = EtapeWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        type_workflow_id = self.kwargs.get('type_workflow_id')
        return EtapeWorkflow.objects.filter(
            type_workflow_id=type_workflow_id
        ).order_by('ordre')


class InstanceWorkflowListView(generics.ListAPIView):
    """Liste les instances de workflows."""
    serializer_class = InstanceWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['type_workflow', 'statut', 'priorite', 'departement']
    search_fields = ['reference_patient', 'notes']
    ordering_fields = ['demarre_le', 'priorite', 'statut']
    ordering = ['-demarre_le']
    
    def get_queryset(self):
        queryset = InstanceWorkflow.objects.select_related(
            'type_workflow', 'etape_actuelle', 'departement', 'initie_par'
        )
        
        # Filtrer par statut "en cours" par défaut
        statut = self.request.query_params.get('statut')
        if not statut:
            queryset = queryset.filter(
                statut__in=['INITIE', 'EN_COURS', 'EN_PAUSE']
            )
        
        # Filtrer par département de l'utilisateur si personnel médical
        utilisateur = self.request.user
        if utilisateur.is_medical_staff and utilisateur.department:
            queryset = queryset.filter(departement=utilisateur.department)
        
        return queryset


class InstanceWorkflowDetailView(generics.RetrieveAPIView):
    """Détails d'une instance de workflow avec historique."""
    queryset = InstanceWorkflow.objects.all()
    serializer_class = InstanceWorkflowDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class DemarrerWorkflowView(APIView):
    """Endpoint pour démarrer un nouveau workflow."""
    permission_classes = [permissions.IsAuthenticated, IsMedicalStaff]
    
    def post(self, request):
        serializer = DemarrerWorkflowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = GestionWorkflowService()
        
        try:
            instance = service.demarrer_workflow(
                type_workflow_id=serializer.validated_data['type_workflow'],
                reference_patient=serializer.validated_data['reference_patient'],
                departement_id=serializer.validated_data['departement'],
                utilisateur=request.user,
                priorite=serializer.validated_data.get('priorite', 'NORMALE'),
                notes=serializer.validated_data.get('notes', '')
            )
            
            return Response({
                'message': 'Workflow démarré avec succès.',
                'instance': InstanceWorkflowSerializer(instance).data
            }, status=status.HTTP_201_CREATED)
            
        except WorkflowException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AvancerEtapeView(APIView):
    """Endpoint pour faire avancer le workflow à l'étape suivante."""
    permission_classes = [permissions.IsAuthenticated, IsMedicalStaff]
    
    def post(self, request, pk):
        serializer = AvancerEtapeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = GestionWorkflowService()
        
        try:
            instance = service.avancer_etape(
                instance_id=pk,
                utilisateur=request.user,
                commentaire=serializer.validated_data.get('commentaire', '')
            )
            
            message = 'Workflow terminé.' if instance.statut == 'TERMINE' else 'Étape suivante activée.'
            
            return Response({
                'message': message,
                'instance': InstanceWorkflowSerializer(instance).data
            })
            
        except WorkflowException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AbandonnerWorkflowView(APIView):
    """Endpoint pour abandonner un workflow."""
    permission_classes = [permissions.IsAuthenticated, IsMedicalStaff]
    
    def post(self, request, pk):
        serializer = AbandonnerWorkflowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = GestionWorkflowService()
        
        try:
            instance = service.abandonner_workflow(
                instance_id=pk,
                utilisateur=request.user,
                raison=serializer.validated_data['raison']
            )
            
            return Response({
                'message': 'Workflow abandonné.',
                'instance': InstanceWorkflowSerializer(instance).data
            })
            
        except WorkflowException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PauseRepriseWorkflowView(APIView):
    """Endpoint pour mettre en pause ou reprendre un workflow."""
    permission_classes = [permissions.IsAuthenticated, IsMedicalStaff]
    
    def post(self, request, pk, action):
        service = GestionWorkflowService()
        
        try:
            if action == 'pause':
                instance = service.mettre_en_pause(pk)
                message = 'Workflow mis en pause.'
            elif action == 'reprendre':
                instance = service.reprendre(pk)
                message = 'Workflow repris.'
            else:
                return Response({
                    'erreur': 'Action invalide. Utilisez "pause" ou "reprendre".'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'message': message,
                'instance': InstanceWorkflowSerializer(instance).data
            })
            
        except WorkflowException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProgressionWorkflowView(APIView):
    """Endpoint pour obtenir la progression d'un workflow."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        service = GestionWorkflowService()
        
        try:
            progression = service.obtenir_progression_workflow(pk)
            return Response(progression)
            
        except WorkflowException as e:
            return Response({
                'erreur': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


class WorkflowsEnRetardView(APIView):
    """Endpoint pour lister les workflows en retard."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        service = GestionWorkflowService()
        instances = service.obtenir_workflows_en_retard()
        
        return Response({
            'nombre': len(instances),
            'workflows': InstanceWorkflowSerializer(instances, many=True).data
        })
