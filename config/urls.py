from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('shop.urls')),
    path('api/', include('cart.urls')),
    path('api/', include('orders.urls')),
]
