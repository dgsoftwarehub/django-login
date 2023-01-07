"""Serializers for orders."""

from rest_framework import serializers
from orders.models import UserBalance, UserBalanceHistory, Order, OrderSMS


class CreateOrderSerializer(serializers.ModelSerializer):
    """Create order for user."""

    class Meta:
        model = Order
        fields = ['country', 'service', 'user', 'amount', ]


class ListOrderSerializer(serializers.ModelSerializer):
    """Create order for user."""
    sms_codes = serializers.SerializerMethodField()

    def get_sms_codes(self, obj):
        return obj.sms_codes.values_list('sms_code', flat=True)

    class Meta:
        model = Order
        fields = ['id', 'country', 'service', 'activation_id', 'number', 'status', 'created_at', 'amount', 'sms_codes']


class UserBalanceAddSerializer(serializers.ModelSerializer):
    """Add User balance."""

    class Meta:
        model = UserBalance
        fields = ['amount', ]


class UserBalanceHistorySerializer(serializers.ModelSerializer):
    """User's balance history."""

    class Meta:
        model = UserBalanceHistory
        fields = ['created_at', 'amount', ]
