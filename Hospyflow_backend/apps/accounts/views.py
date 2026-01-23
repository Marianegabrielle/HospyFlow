from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from .models import Department
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    DepartmentSerializer,
    CustomTokenObtainPairSerializer
)
from .permissions import IsAdminUser

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT login view with user info in response."""
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Utilisateur créé avec succès.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Current user profile endpoint."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordView(APIView):
    """Change password endpoint."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'error': 'Mot de passe actuel incorrect.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Mot de passe modifié avec succès.'
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """List all users (admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    filterset_fields = ['role', 'department', 'is_active', 'is_on_duty']
    search_fields = ['email', 'first_name', 'last_name', 'employee_id']
    ordering_fields = ['created_at', 'last_name', 'role']


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """User detail/update/delete endpoint (admin only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class DepartmentListCreateView(generics.ListCreateAPIView):
    """List and create departments."""
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_active', 'building', 'floor']
    search_fields = ['name', 'code', 'description']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.IsAuthenticated()]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Department detail/update/delete endpoint."""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]


class StaffByDepartmentView(generics.ListAPIView):
    """List staff members by department."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        department_id = self.kwargs.get('department_id')
        return User.objects.filter(
            department_id=department_id,
            is_active=True
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_duty_status(request):
    """Toggle user's on-duty status."""
    user = request.user
    user.is_on_duty = not user.is_on_duty
    user.save()
    
    return Response({
        'message': f"Statut de service mis à jour.",
        'is_on_duty': user.is_on_duty
    })
