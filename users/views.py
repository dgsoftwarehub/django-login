"""Views for users.

Includes views for:
    1. SignUp
    2. SignIn
    3. Profile View and Update
    4. Sign Out
"""

from django.contrib.auth.hashers import (
    check_password,
    make_password,
)
from django.contrib.auth import authenticate

from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_200_OK, HTTP_406_NOT_ACCEPTABLE, HTTP_400_BAD_REQUEST
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from users.serializers import SignUpSerializer, SignInSerializer, ProfileDisplaySerializer, ChangePasswordSerializer
from users.permissions import IsLoggedIn
from users.models import UserAPIKey , User


class SignupView(CreateAPIView):
    """Create a User."""
    print("non")
    serializer_class = SignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        serializer.save()
        user_inital = User.objects.filter(email=email).first()
        token, created = Token.objects.get_or_create(user= user_inital)
        return Response({'token': token.key, 'email' : email})
        

class SignInView(ObtainAuthToken):
    """Sign In User."""
    serializer_class = SignInSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'balance': user.balance.amount})


class ProfileUpdateView(IsLoggedIn, RetrieveUpdateAPIView):
    """Display and update User's profile."""

    serializer_class = ProfileDisplaySerializer

    def get_object(self):
        """Return object instance."""
        return self.request.user


class GetAPIKeyView(IsLoggedIn, APIView):
    """Get API key for user."""

    def get(self, request):
        """Get API key for user."""
        user = request.user
        UserAPIKey.objects.filter(user=user).delete()
        _, key = UserAPIKey.objects.create_key(user=user, prefix=user.email, name=f'Key for {user.email}')
        return Response(status=HTTP_200_OK, data={'key': key})


class ChangePasswordView(IsLoggedIn, APIView):
    """Change password for users."""

    @staticmethod
    def get_passwords(request_data):
        """Get and validate password data."""
        password_serializer = ChangePasswordSerializer(data=request_data)
        is_valid = password_serializer.is_valid()
        return is_valid, (password_serializer.data if is_valid else password_serializer.errors)

    def post(self, request):
        """Change password for users."""
        is_valid, passwords = self.get_passwords(request.data)
        if is_valid is False:
            return Response(status=HTTP_400_BAD_REQUEST, data=passwords)
        if check_password(passwords['old_password'], request.user.password):
            request.user.password = make_password(passwords['password'])
            request.user.save()
            return Response(status=HTTP_200_OK, data={'message': 'Password Updated!'})
        else:
            return Response(status=HTTP_406_NOT_ACCEPTABLE, data={'message': 'Old Password does not match.'})


class SignOutView(IsLoggedIn, APIView):
    """Sign Out User."""

    def get(self, request):
        """Sign Out User on Get Request."""
        request.user.auth_token.delete()
        return Response(status=HTTP_200_OK)
