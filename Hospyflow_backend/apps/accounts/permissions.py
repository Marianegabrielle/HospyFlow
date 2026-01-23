from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permission class for admin users only."""
    
    message = "Seuls les administrateurs peuvent effectuer cette action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'ADMIN' or request.user.is_superuser
        )


class IsMedicalStaff(permissions.BasePermission):
    """Permission class for medical staff (nurses, doctors, lab techs)."""
    
    message = "Seul le personnel médical peut effectuer cette action."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role in ['NURSE', 'DOCTOR', 'LAB_TECH'] or
            request.user.is_superuser
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission class for owner or admin."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role == 'ADMIN':
            return True
        
        # Check if object has a user/reporter field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'reporter'):
            return obj.reporter == request.user
        
        return False
