from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    UserProfileView,
    ChangePasswordView,
    UserListView,
    UserDetailView,
    DepartmentListCreateView,
    DepartmentDetailView,
    StaffByDepartmentView,
    toggle_duty_status
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('me/toggle-duty/', toggle_duty_status, name='toggle_duty'),
    
    # User management (admin)
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    
    # Departments
    path('departments/', DepartmentListCreateView.as_view(), name='department_list'),
    path('departments/<int:pk>/', DepartmentDetailView.as_view(), name='department_detail'),
    path('departments/<int:department_id>/staff/', StaffByDepartmentView.as_view(), name='department_staff'),
]
