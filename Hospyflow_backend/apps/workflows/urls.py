from django.urls import path

from .views import (
    TypeWorkflowListView,
    TypeWorkflowDetailView,
    TypeWorkflowCreateUpdateView,
    EtapeWorkflowListView,
    InstanceWorkflowListView,
    InstanceWorkflowDetailView,
    DemarrerWorkflowView,
    AvancerEtapeView,
    AbandonnerWorkflowView,
    PauseRepriseWorkflowView,
    ProgressionWorkflowView,
    WorkflowsEnRetardView
)

urlpatterns = [
    # Types de workflows
    path('types/', TypeWorkflowListView.as_view(), name='type_workflow_list'),
    path('types/<int:pk>/', TypeWorkflowDetailView.as_view(), name='type_workflow_detail'),
    path('types/creer/', TypeWorkflowCreateUpdateView.as_view(), name='type_workflow_create'),
    path('types/<int:pk>/modifier/', TypeWorkflowCreateUpdateView.as_view(), name='type_workflow_update'),
    path('types/<int:type_workflow_id>/etapes/', EtapeWorkflowListView.as_view(), name='etapes_workflow'),
    
    # Instances de workflows
    path('instances/', InstanceWorkflowListView.as_view(), name='instance_workflow_list'),
    path('instances/<int:pk>/', InstanceWorkflowDetailView.as_view(), name='instance_workflow_detail'),
    path('instances/<int:pk>/progression/', ProgressionWorkflowView.as_view(), name='progression_workflow'),
    
    # Actions sur les workflows
    path('demarrer/', DemarrerWorkflowView.as_view(), name='demarrer_workflow'),
    path('instances/<int:pk>/avancer/', AvancerEtapeView.as_view(), name='avancer_etape'),
    path('instances/<int:pk>/abandonner/', AbandonnerWorkflowView.as_view(), name='abandonner_workflow'),
    path('instances/<int:pk>/<str:action>/', PauseRepriseWorkflowView.as_view(), name='pause_reprise_workflow'),
    
    # Surveillance
    path('en-retard/', WorkflowsEnRetardView.as_view(), name='workflows_en_retard'),
]
