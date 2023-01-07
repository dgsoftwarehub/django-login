import environ
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import permissions, authentication, exceptions
from users.models import UserAPIKey
from orders.models import SMSHistory

env = environ.Env()
environ.Env.read_env()


class IsLoggedIn:
    """Check if user is logged in."""
    authentication_classes = [authentication.TokenAuthentication, ]
    permission_classes = [permissions.IsAuthenticated, ]


class UserHasAPIKey(HasAPIKey):
    """Permission to check if the key is valid."""

    model = UserAPIKey

    def __init__(self, *args, **kwargs):
        self.key_parser.keyword = 'Bearer'


class IsUserAPI:
    """Check if user has valid API key."""

    permission_classes = [UserHasAPIKey, ]


class SMSSenderKeyAuthentication(authentication.BaseAuthentication):
    """Authenticate if request is from our trusted API sender."""

    @staticmethod
    def _add_to_history(request):
        """Record request params."""
        SMSHistory.objects.create(request_data=request.data)

    def authenticate(self, request):
        """Check if key sent in header is valid."""
        key = request.META.get("HTTP_AUTHORIZATION", '').split()[1]
        if key != env('SMS_KEY', default=''):
            raise exceptions.AuthenticationFailed

        self._add_to_history(request)
