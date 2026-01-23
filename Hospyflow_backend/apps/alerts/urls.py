from django.urls import path

from .views import (
    AlerteListView,
    AlerteDetailView,
    MesAlertesView,
    AcquitterAlerteView,
    ResoudreAlerteView,
    IgnorerAlerteView,
    RegleAlerteListCreateView,
    RegleAlerteDetailView,
    EvaluerReglesView,
    MesAbonnementsView,
    CreerAbonnementView,
    SupprimerAbonnementView
)

urlpatterns = [
    # Alertes
    path('', AlerteListView.as_view(), name='alerte_list'),
    path('<int:pk>/', AlerteDetailView.as_view(), name='alerte_detail'),
    path('mes-alertes/', MesAlertesView.as_view(), name='mes_alertes'),
    path('<int:pk>/acquitter/', AcquitterAlerteView.as_view(), name='acquitter_alerte'),
    path('<int:pk>/resoudre/', ResoudreAlerteView.as_view(), name='resoudre_alerte'),
    path('<int:pk>/ignorer/', IgnorerAlerteView.as_view(), name='ignorer_alerte'),
    
    # Règles d'alerte (admin)
    path('regles/', RegleAlerteListCreateView.as_view(), name='regle_list'),
    path('regles/<int:pk>/', RegleAlerteDetailView.as_view(), name='regle_detail'),
    path('regles/evaluer/', EvaluerReglesView.as_view(), name='evaluer_regles'),
    
    # Abonnements
    path('abonnements/', MesAbonnementsView.as_view(), name='mes_abonnements'),
    path('abonnements/creer/', CreerAbonnementView.as_view(), name='creer_abonnement'),
    path('abonnements/<int:pk>/', SupprimerAbonnementView.as_view(), name='supprimer_abonnement'),
]
