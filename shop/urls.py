from django.urls import path
from .views import (
    CategoryListView, ContactDeleteView, ContactListCreateView, PartnerStateView,
    PartnerUpdateView, ProductDetailView, ProductInfoView, ProductListView, ShopListView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('product-info/<int:pk>/', ProductInfoView.as_view(), name='product-info'),
    path('shops/', ShopListView.as_view(), name='shops'),
    path('contacts/', ContactListCreateView.as_view(), name='contacts'),
    path('contacts/<int:pk>/', ContactDeleteView.as_view(), name='contact-delete'),
    path('partner/update/', PartnerUpdateView.as_view(), name='partner-update'),
    path('partner/state/', PartnerStateView.as_view(), name='partner-state'),
]
