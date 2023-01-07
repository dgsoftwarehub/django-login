"""URLs for User."""

from django.urls import path
from orders.views import (
    BalanceAddView,
    BalanceHistoryView,
    CancelOrderView,
    CreateAppOrderView,
    CreateUserOrderView,
    ListOrderView,
    UpdateSMSView,
    FinishOrderView,
    ListActiveOrdersView
)

app_name = 'orders'

urlpatterns = [
    path('app_place', CreateAppOrderView.as_view(), name='place-app-order'),
    path('user_place', CreateUserOrderView.as_view(), name='place-user-order'),
    path('list', ListOrderView.as_view(), name='list-orders'),
    path('list_active', ListActiveOrdersView.as_view(), name='list-active-orders'),
    path('add_balance', BalanceAddView.as_view(), name='add-balance'),
    path('balance_history', BalanceHistoryView.as_view(), name='balance-history'),
    path('cancel/<int:order_id>', CancelOrderView.as_view(), name='cancel-order'),
    path('finish/<int:order_id>', FinishOrderView.as_view(), name='finish-order'),
    path('push_sms', UpdateSMSView.as_view(), name='push-sms'),
]
