"""Models for users.

Includes models:
    1. User model
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import EmailValidator
from rest_framework_api_key.models import AbstractAPIKey
from users.managers import UserManager


class User(AbstractBaseUser):
    """Custom User model that uses email instead of username."""

    email = models.EmailField(
        verbose_name='email address', max_length=175,
        unique=True, validators=[EmailValidator, ]
    )
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        """Represent instance of this class."""
        return self.email

    def has_perm(self, perm: str, obj: object = None):
        """Check for specific permission."""
        return True

    def has_module_perms(self, app_label: str):
        """Check user permission to view app_label."""
        return True

    # def save(self, *args, **kwargs):
    #     user = super().save(args, kwargs)
    #     # UserAPIKey.objects.create_key(user=user, prefix=email, name=f'Key for {email}')
    #     return user


class UserAPIKey(AbstractAPIKey):
    """API keys for users to get numbers."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='api_key')
    prefix = models.CharField(max_length=175, unique=True, editable=False)
