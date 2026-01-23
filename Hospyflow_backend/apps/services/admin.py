from django.contrib import admin
from .models import ServiceHospitalier


@admin.register(ServiceHospitalier)
class ServiceHospitalierAdmin(admin.ModelAdmin):
    list_display = ['department', 'etat', 'saturation', 'derniere_maj']
    list_filter = ['etat', 'derniere_maj']
    search_fields = ['department__name', 'department__code']
    readonly_fields = ['saturation', 'derniere_maj']
    
    fieldsets = (
        (None, {
            'fields': ('department', 'etat')
        }),
        ('Métriques', {
            'fields': ('saturation', 'derniere_maj'),
            'classes': ('collapse',)
        }),
    )
