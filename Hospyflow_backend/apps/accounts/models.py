from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for HospyFlow users."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Le superutilisateur doit avoir is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class Department(models.Model):
    """Hospital department/service model."""
    
    name = models.CharField(_('Nom'), max_length=100)
    code = models.CharField(_('Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    floor = models.CharField(_('Étage'), max_length=20, blank=True)
    building = models.CharField(_('Bâtiment'), max_length=50, blank=True)
    is_active = models.BooleanField(_('Actif'), default=True)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Département')
        verbose_name_plural = _('Départements')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class User(AbstractUser):
    """Custom user model for HospyFlow."""
    
    class Role(models.TextChoices):
        NURSE = 'NURSE', _('Infirmier(ère)')
        DOCTOR = 'DOCTOR', _('Médecin')
        LAB_TECH = 'LAB_TECH', _('Technicien de laboratoire')
        ADMIN = 'ADMIN', _('Administrateur')
    
    username = None  # Remove username field
    email = models.EmailField(_('Adresse email'), unique=True)
    first_name = models.CharField(_('Prénom'), max_length=150)
    last_name = models.CharField(_('Nom de famille'), max_length=150)
    role = models.CharField(
        _('Rôle'),
        max_length=20,
        choices=Role.choices,
        default=Role.NURSE
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff',
        verbose_name=_('Département')
    )
    employee_id = models.CharField(
        _('Matricule'),
        max_length=50,
        blank=True
    )
    phone_number = models.CharField(
        _('Numéro de téléphone'),
        max_length=20,
        blank=True
    )
    profile_picture = models.ImageField(
        _('Photo de profil'),
        upload_to='profiles/',
        blank=True,
        null=True
    )
    is_on_duty = models.BooleanField(_('En service'), default=False)
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_medical_staff(self):
        return self.role in [self.Role.NURSE, self.Role.DOCTOR, self.Role.LAB_TECH]
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
