import environ
from django.db.models.signals import post_save
from django_rest_passwordreset.signals import reset_password_token_created
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.urls import reverse
from orders.models import UserBalance
from orders.utils import send_emails

env = environ.Env()
environ.Env.read_env()


@receiver(post_save, sender=get_user_model())
def create_balance(sender, instance, created, **kwargs):
    if created:
        UserBalance.objects.create(user=instance)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """Send email on password reset request."""
    url = env('PASS_RESET_URL', default='') or instance.request.build_absolute_uri(reverse(
        'users:password_reset:reset-password-confirm'
    ))

    send_emails(
        env('EMAIL_FROM', default=''),
        reset_password_token.user.email,
        'Password reset request',
        '<strong>{}?token={}</strong>'.format(url, reset_password_token.key)
    )
