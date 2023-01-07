from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save


class UserManager(BaseUserManager):
    """Manager used to create users and superusers for our custom User model."""

    use_in_migrations = True

    def create_users(self, email: str, password: str = None, first_name: str = None,
                     last_name: str = None, number: str = None):
        """Create user instance."""
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str = None, first_name: str = None,
                    last_name: str = None, number: str = None):
        """Create normal user instance."""
        return self.create_users(email, password, first_name, last_name, number)

    def create_staff(self, email: str, password: str = None, first_name: str = None,
                     last_name: str = None, number: str = None):
        """Create staff user instance."""
        user = self.create_users(email, password, first_name, last_name, number)
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str):
        """For creating super user."""
        user = self.create_users(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
