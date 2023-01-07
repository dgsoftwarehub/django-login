from datetime import timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class UserBalance(models.Model):
    """Balance for every user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance', primary_key=True)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0.0), ])

    @staticmethod
    def update_balance(user, amount):
        """Update balance for user."""
        with transaction.atomic():
            user.balance.amount += amount
            user.balance.save()
        return user.balance.amount

    @staticmethod
    def has_balance(user, amount):
        """Check if a user has sufficient balance."""
        with transaction.atomic():
            return True if user.balance.amount >= amount else False


class UserBalanceHistory(models.Model):
    """Balance history for every user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balance_history')
    created_at = models.DateTimeField(default=timezone.now)
    amount = models.FloatField(validators=[MinValueValidator(0.0), ])


class Order(models.Model):
    """User orders."""

    class NumberStatus(models.TextChoices):
        SMS_PENDING = _('sms pending')
        SUCCESS = _('success')
        FINISHED = _('finished')
        EXPIRED = _('expired')
        CANCELLED = _('cancelled')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_orders')
    country = models.CharField(max_length=30)
    service = models.CharField(max_length=10)
    activation_id = models.CharField(blank=True, null=True, max_length=100)
    number = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=15, choices=NumberStatus.choices, default=NumberStatus.SMS_PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    amount = models.FloatField(validators=[MinValueValidator(0.0), ])

    def has_expired(self):
        """Check if 20 minutes has been passed since order creation."""
        return self.created_at + timedelta(minutes=20) < timezone.now()

    def cancel(self):
        """Cancel order if not expired, otherwise expire order."""
        amount = self.user.balance.amount
        status = self.NumberStatus.CANCELLED

        if self.status != self.NumberStatus.SMS_PENDING:
            return amount, self.status
        if self.has_expired():
            status = self.NumberStatus.EXPIRED

        with transaction.atomic():
            self.status = status
            self.save()
        amount = UserBalance.update_balance(self.user, self.amount)
        print(amount)
        return amount, self.status

    def finish(self):
        """Finish an order."""
        if self.status != self.NumberStatus.SUCCESS:
            return self.status
        if self.status == self.NumberStatus.FINISHED:
            return self.status
        with transaction.atomic():
            self.status = self.NumberStatus.FINISHED
            self.save()


class OrderSMS(models.Model):
    """Record history of SMS codes received by third party."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sms_codes')
    sms_code = models.CharField(max_length=255, null=True, blank=True)


class SMSHistory(models.Model):
    """Record history of SMS codes received by third party."""

    request_data = models.JSONField()
