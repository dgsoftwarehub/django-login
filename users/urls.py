"""URLs for User."""

from django.urls import path, include
from users.views import (
    SignupView,
    SignInView,
    ProfileUpdateView,
    SignOutView,
    GetAPIKeyView,
 
       ChangePasswordView,
)

app_name = 'users'

urlpatterns = [
    path('signup', SignupView.as_view(), name='sign-up'),
    path('signin', SignInView.as_view(), name='sign-in'),
    path('signout', SignOutView.as_view(), name='sign-out'),
    path('update', ProfileUpdateView.as_view(), name='profile'),
    path('key', GetAPIKeyView.as_view(), name='profile'),
    path('change_password', ChangePasswordView.as_view(), name='change-password'),
    path('reset_password', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
