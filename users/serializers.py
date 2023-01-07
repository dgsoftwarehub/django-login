"""Serializers for users.

Includes serializers for:
    1. Signing up a user
    2. Sign in a user
    3. Displaying a user's information
    4. Updating a user

"""

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from users.models import User

class SignUpSerializer(serializers.ModelSerializer):
    """Create a User."""

    email = serializers.CharField(style={'input_type': 'email'}, write_only=True,
                                     required=True)

    password = serializers.CharField(style={'input_type': 'password'}, write_only=True,
                                     required=True, validators=[validate_password])
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True,
                                             required=True, validators=[validate_password])

    def validate(self, attrs):
        """Check if passwords match."""
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists!")
        return value       

    def create(self, validated_data):
        """Create user with all validated data."""
        validated_data.pop('confirm_password')
        user = get_user_model().objects.create_user(**validated_data)
        
        print("done",type(user))
        print(str(user))
        return str(user)
        
        
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'confirm_password']


class SignInSerializer(serializers.Serializer):
    """Log In User."""

    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    def validate(self, attrs):
        """Validate user's inputs."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError('Not authenticated', code='authentication')

        attrs['user'] = user
        return attrs


class ProfileDisplaySerializer(serializers.ModelSerializer):
    """Display User information."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name']


class ChangePasswordSerializer(serializers.Serializer):
    """Change password for user."""

    old_password = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def is_valid(self, raise_exception=False):
        is_data_valid = super().is_valid(raise_exception)
        if self._validated_data.get('password') != self._validated_data.get('confirm_password'):
            self._errors['confirm_password'] = 'Passwords do not match'
            is_data_valid = False
            if raise_exception:
                raise ValidationError()

        return is_data_valid

    class Meta:
        fields = ['old_password', 'password', 'confirm_password']
