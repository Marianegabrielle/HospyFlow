from django.urls import path

from .views import (
    CategorieEvenementListView,
    MicroEvenementListView,
    MicroEvenementDetailView,
    MesEvenementsView,
    EvenementsCritiquesView,
    EvenementsRecentsView,
    SignalerEvenementView,
    PrendreEnChargeView,
    ResoudreEvenementView,
    AjouterCommentaireView,
    MarquerRecurrentView,
    StatistiquesEvenementsView,
    TendancesEvenementsView
)

urlpatterns = [
    # Catégories
    path('categories/', CategorieEvenementListView.as_view(), name='categorie_list'),
    
    # Liste et détails des événements
    path('', MicroEvenementListView.as_view(), name='evenement_list'),
    path('<int:pk>/', MicroEvenementDetailView.as_view(), name='evenement_detail'),
    path('mes-evenements/', MesEvenementsView.as_view(), name='mes_evenements'),
    path('critiques/', EvenementsCritiquesView.as_view(), name='evenements_critiques'),
    path('recents/', EvenementsRecentsView.as_view(), name='evenements_recents'),
    
    # Actions sur les événements
    path('signaler/', SignalerEvenementView.as_view(), name='signaler_evenement'),
    path('<int:pk>/prendre-en-charge/', PrendreEnChargeView.as_view(), name='prendre_en_charge'),
    path('<int:pk>/resoudre/', ResoudreEvenementView.as_view(), name='resoudre_evenement'),
    path('<int:pk>/commenter/', AjouterCommentaireView.as_view(), name='ajouter_commentaire'),
    path('<int:pk>/marquer-recurrent/', MarquerRecurrentView.as_view(), name='marquer_recurrent'),
    
    # Statistiques
    path('statistiques/', StatistiquesEvenementsView.as_view(), name='statistiques_evenements'),
    path('tendances/', TendancesEvenementsView.as_view(), name='tendances_evenements'),
]
