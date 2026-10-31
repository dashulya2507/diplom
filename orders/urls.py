from django.urls import path
from .views import (
    OrderListView, OrderDetailView, OrderCreateView, OrderStatusView,
    PartnerOrderListView,
)

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusView.as_view(), name='order-status'),
    path('partner/orders/', PartnerOrderListView.as_view(), name='partner-orders'),
]
