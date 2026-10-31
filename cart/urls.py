from django.urls import path
from .views import CartListView,CartAddView,CartDeleteView
urlpatterns=[path('cart/',CartListView.as_view()),path('cart/add/',CartAddView.as_view()),path('cart/<int:pk>/',CartDeleteView.as_view())]
