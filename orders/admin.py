from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dt', 'state', 'contact', 'total_display')
    list_filter = ('state', 'dt')
    search_fields = ('user__email',)
    list_editable = ('state',)

    @admin.display(description='Сумма')
    def total_display(self, obj):
        return obj.total()

    def save_model(self, request, obj, form, change):
        old_state = None
        if change and obj.pk:
            old_state = Order.objects.get(pk=obj.pk).state
        super().save_model(request, obj, form, change)
        if change and old_state != obj.state:
            send_mail(
                f'Статус заказа #{obj.id}',
                f'Статус вашего заказа изменён: {obj.get_state_display()}',
                settings.DEFAULT_FROM_EMAIL,
                [obj.user.email],
                fail_silently=True,
            )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info', 'quantity', 'price')
