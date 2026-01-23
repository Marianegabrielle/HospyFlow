from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Department

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model."""
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'floor', 'building', 'is_active']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    department_detail = DepartmentSerializer(source='department', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'department', 'department_detail',
            'employee_id', 'phone_number', 'profile_picture',
            'is_on_duty', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'department',
            'employee_id', 'phone_number'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Les mots de passe ne correspondent pas."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'department',
            'employee_id', 'phone_number', 'profile_picture', 'is_on_duty'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Les nouveaux mots de passe ne correspondent pas."
            })
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user info."""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra user information to the response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.get_full_name(),
            'role': self.user.role,
            'role_display': self.user.get_role_display(),
            'department': self.user.department.name if self.user.department else None,
            'is_admin': self.user.is_admin,
        }
        
        return data
