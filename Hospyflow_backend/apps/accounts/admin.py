from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'floor', 'building', 'is_active']
    list_filter = ['is_active', 'building']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'department', 'is_on_duty', 'is_active']
    list_filter = ['role', 'department', 'is_on_duty', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'employee_id']
    ordering = ['last_name', 'first_name']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')
        }),
        (_('Informations professionnelles'), {
            'fields': ('role', 'department', 'employee_id', 'is_on_duty')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'department', 'password1', 'password2'),
        }),
    )
