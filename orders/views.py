"""Views for orders."""

from abc import ABC, abstractmethod
import requests

import environ
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView, ListAPIView
from rest_framework.response import Response

from orders.serializers import (
    UserBalanceAddSerializer,
    UserBalanceHistorySerializer,
    CreateOrderSerializer,
    ListOrderSerializer
)
from orders.models import UserBalance, UserBalanceHistory, Order, OrderSMS
from users.permissions import IsLoggedIn, IsUserAPI, SMSSenderKeyAuthentication
from users.models import UserAPIKey

env = environ.Env()
environ.Env.read_env()


class CreateOrderView(APIView, ABC):
    """Create order for user."""

    user = None

    @abstractmethod
    def set_user(self):
        """Set user after authentication."""
        pass

    def create_data(self, request):
        """Create order from request."""
        def extract_data(key):
            return request.data[key].lower() if key in request.data.keys() else None

        data = {
            'country': extract_data('country'),
            'service': extract_data('service'),
            'user': self.user.id,
            'amount': request.data.get('amount')
        }
        return CreateOrderSerializer(data=data)

    def create_order(self, response, order_serializer):
        """Create order entry after successful API call."""
        response_data = response.json()
        with transaction.atomic():
            order = order_serializer.save()
            order.activation_id = response_data['activationId']
            order.number = response_data['number']
            order.save()

        remaining_balance = UserBalance.update_balance(self.user, order_serializer.validated_data['amount'] * -1)
        return Response(status=HTTP_200_OK, data={
            'amount': remaining_balance,
            'number': order.number,
            'activationID': order.activation_id
        })

    def order_number(self, order_serializer):
        """Call the order API to get number and details."""
        response = requests.post(
            env('ORDER_API'),
            json={
                'service': order_serializer.validated_data['service'],
                'country': order_serializer.validated_data['country']
            }
        )

        if response.status_code == 200:
            return self.create_order(response, order_serializer)
        print(response.text)
        return Response(status=response.status_code, data={
            'message': 'Error in acquiring number. This might be because the service or country is not correct.'
        })

    def post(self, request):
        """Order a number for user."""
        self.set_user()
        order_serializer = self.create_data(request)

        if not order_serializer.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST, data=order_serializer.errors)
        if not UserBalance.has_balance(self.user, order_serializer.validated_data['amount']):
            return Response(status=HTTP_406_NOT_ACCEPTABLE, data={'message': 'Insufficient funds'})
        return self.order_number(order_serializer)


class CreateAppOrderView(IsLoggedIn, CreateOrderView):
    """Handle order creation requests from frontend app."""
    """There is no need to pass Token to complete this project. """
    def set_user(self):
        """Set user for this instance."""
        self.user = self.request.user


class CreateUserOrderView(IsUserAPI, CreateOrderView):
    """Handle order creation requests from API key."""

    def set_user(self):
        """Set user for this instance."""
        key = self.request.META["HTTP_AUTHORIZATION"].split()[1]
        user_key = UserAPIKey.objects.get_from_key(key)
        self.user = user_key.user


class ListOrderView(IsLoggedIn, ListAPIView):
    """List orders."""

    serializer_class = ListOrderSerializer

    def get_queryset(self):
        """Get list of user's orders."""
        return Order.objects.filter(user=self.request.user)

    def filter_queryset(self, queryset):
        """Expire orders if required."""
        for order in queryset:
            if order.has_expired():
                order.cancel()
        return queryset

    def list(self, request, *args, **kwargs):
        """List orders."""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = []
        for x in serializer.data:
            print(x,dict(x))
            data.append(dict(x))
        print(data)
        data.sort(key=lambda x:x['created_at'])

        return Response({'balance': request.user.balance.amount, 'orders': data[::-1]})


class ListActiveOrdersView(ListOrderView):
    """List active orders."""

    def get_queryset(self):
        """Get orders with sms_pending and success status."""
        filter_statuses = [Order.NumberStatus.SMS_PENDING, Order.NumberStatus.SUCCESS]
        return Order.objects.filter(user=self.request.user, status__in=filter_statuses)


class CancelOrderView(IsLoggedIn, APIView):
    """Cancel order for user."""

    def update_data(self, order):
        """Update order status and balance."""
        remaining_amount, status = order.cancel()
        return Response(status=HTTP_200_OK, data={'balance': remaining_amount, 'status': status})

    def get(self, request, order_id):
        """Cancel order for a user if they did not receive a number and time after order is less than 20 minutes."""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND, data={'message': 'Order Not Found'})

        if order.status == Order.NumberStatus.SUCCESS:
            return Response(
                status=HTTP_406_NOT_ACCEPTABLE,
                data={'message': 'Order is already successful'}
            )

        if order.status == Order.NumberStatus.FINISHED:
            return Response(
                status=HTTP_406_NOT_ACCEPTABLE,
                data={'message': 'Order is already finished'}
            )

        return self.update_data(order)


class FinishOrderView(IsLoggedIn, APIView):
    """Finish order for user."""

    @staticmethod
    def update_data(order):
        """Update order status"""
        order.finish()
        return Response(status=HTTP_200_OK, data={'status': order.status})

    def get(self, request, order_id):
        """Finish order for a user if it is already successful."""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND, data={'message': 'Order Not Found'})

        if order.status == Order.NumberStatus.CANCELLED:
            return Response(
                status=HTTP_406_NOT_ACCEPTABLE,
                data={'message': 'Order is already cancelled'}
            )

        if order.status == Order.NumberStatus.EXPIRED:
            return Response(
                status=HTTP_406_NOT_ACCEPTABLE,
                data={'message': 'Order is already expired'}
            )

        if order.status == Order.NumberStatus.SMS_PENDING:
            return Response(
                status=HTTP_406_NOT_ACCEPTABLE,
                data={'message': 'SMS still pending for order'}
            )

        return self.update_data(order)


class UpdateSMSView(APIView):
    """Update SMS from third party service."""

    authentication_classes = [SMSSenderKeyAuthentication, ]

    def post(self, request):
        """Update SMS code and status against order."""
        if 'activationId' not in request.data.keys() or 'text' not in request.data.keys():
            return Response(status=HTTP_400_BAD_REQUEST, data={'activationId': 'Missing parameters'})

        try:
            order = Order.objects.get(activation_id=request.data.get('activationId', ''))
        except Order.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND, data={'message': 'Order not found against activation ID'})

        if order.status == Order.NumberStatus.CANCELLED:
            return Response(status=HTTP_200_OK, data={'message': 'Order has already been cancelled'})
        if order.status == Order.NumberStatus.FINISHED:
            return Response(status=HTTP_200_OK, data={'message': 'Order has already been finished'})
        if order.has_expired():
            order.cancel()
            return Response(status=HTTP_200_OK, data={'message': '20 minutes have already passed after order creation'})

        order.status = Order.NumberStatus.SUCCESS
        order.save()
        OrderSMS.objects.create(order=order, sms_code=request.data.get('text', ''))
        return Response(status=HTTP_200_OK, data={'message': 'SMS code added to order'})


class BalanceAddView(IsLoggedIn, UpdateAPIView):
    """Add balance for a user."""

    serializer_class = UserBalanceAddSerializer
    http_method_names = ['patch', ]

    def get_object(self):
        """Retrieve user object."""
        return get_object_or_404(UserBalance, pk=self.request.user)

    def patch(self, request, *args, **kwargs):
        """Add amount in user balance."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if not serializer.validated_data['amount'] > 0:
            return Response(status=HTTP_400_BAD_REQUEST, data={'message': 'Amount should be greater than 0'})

        amount = UserBalance.update_balance(request.user, serializer.validated_data['amount'])
        UserBalanceHistory.objects.create(user=request.user, amount=serializer.validated_data.get('amount'))

        return Response({'amount': amount})


class BalanceHistoryView(IsLoggedIn, ListAPIView):
    """Get list of balance deposits."""

    serializer_class = UserBalanceHistorySerializer

    def get_queryset(self):
        """Get user balance history."""
        return UserBalanceHistory.objects.filter(user=self.request.user)
