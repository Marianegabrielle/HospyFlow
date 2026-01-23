from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceViewSet, TypeFluxViewSet, MicroEvenementViewSet, 
    AlerteViewSet, RapportViewSet
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'flux', TypeFluxViewSet)
router.register(r'evenements', MicroEvenementViewSet)
router.register(r'alertes', AlerteViewSet)
router.register(r'rapports', RapportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
