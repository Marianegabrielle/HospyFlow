"""
URL configuration for HospyFlow project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="HospyFlow - ClinicFlow Analytics API",
        default_version='v1',
        description="""
        API pour l'analyse des flux hospitaliers.
        
        ## Fonctionnalités
        - Authentification JWT
        - Gestion des utilisateurs (Infirmiers, Médecins, Personnel de laboratoire, Administrateurs)
        - Signalement des micro-événements (retards, blocages, incidents)
        - Analyse des goulots d'étranglement
        - Tableaux de bord analytiques
        - Système d'alertes
        """,
        terms_of_service="https://www.hospyflow.com/terms/",
        contact=openapi.Contact(email="contact@hospyflow.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/workflows/', include('apps.workflows.urls')),
    path('api/events/', include('apps.events.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/services/', include('apps.services.urls')),
]

# Admin site customization
admin.site.site_header = "HospyFlow Administration"
admin.site.site_title = "HospyFlow Admin"
admin.site.index_title = "Bienvenue sur HospyFlow - ClinicFlow Analytics"
