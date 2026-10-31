from django.urls import path
from .views import ConfirmEmailView, LoginView, MeView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/confirm/', ConfirmEmailView.as_view(), name='confirm-register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
]
