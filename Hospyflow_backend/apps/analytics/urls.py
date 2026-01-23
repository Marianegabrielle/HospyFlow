from django.urls import path

from .views import (
    TableauBordView,
    GoulotListView,
    GoulotDetailView,
    DetecterGoulotsView,
    ConfirmerGoulotView,
    ResoudreGoulotView,
    MarquerFauxPositifView,
    MetriquesDepartementView,
    MetriquesDepartementDetailView,
    StatistiquesGlobalesView,
    GenererStatistiquesView,
    RapportViewSet
)

urlpatterns = [
    # Tableau de bord principal
    path('tableau-de-bord/', TableauBordView.as_view(), name='tableau_bord'),
    
    # Goulots d'étranglement
    path('goulots/', GoulotListView.as_view(), name='goulot_list'),
    path('goulots/<int:pk>/', GoulotDetailView.as_view(), name='goulot_detail'),
    path('goulots/detecter/', DetecterGoulotsView.as_view(), name='detecter_goulots'),
    path('goulots/<int:pk>/confirmer/', ConfirmerGoulotView.as_view(), name='confirmer_goulot'),
    path('goulots/<int:pk>/resoudre/', ResoudreGoulotView.as_view(), name='resoudre_goulot'),
    path('goulots/<int:pk>/faux-positif/', MarquerFauxPositifView.as_view(), name='faux_positif_goulot'),
    
    # Métriques
    path('metriques/', MetriquesDepartementView.as_view(), name='metriques_list'),
    path('metriques/departement/<int:departement_id>/', MetriquesDepartementDetailView.as_view(), name='metriques_departement'),
    path('statistiques/', StatistiquesGlobalesView.as_view(), name='statistiques_globales'),
    path('statistiques/generer/', GenererStatistiquesView.as_view(), name='generer_statistiques'),
    
    # Rapports (compatible avec ancien backend)
    path('rapports/', RapportViewSet.as_view(), name='rapports'),
]
