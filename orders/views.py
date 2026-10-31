from django.conf import settings
from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from cart.models import CartItem
from shop.models import Contact
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .tasks import send_order_email


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('contact').prefetch_related(
            'ordered_items__product_info__product', 'ordered_items__product_info__shop'
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('contact').prefetch_related(
            'ordered_items__product_info__product', 'ordered_items__product_info__shop'
        )


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        contact_id = request.data.get('contact_id')
        items = list(CartItem.objects.filter(user=request.user).select_related('product_info__product', 'product_info__shop'))
        if not items:
            return Response({'detail': 'Корзина пуста.'}, status=400)
        if not contact_id:
            return Response({'detail': 'Укажите contact_id.'}, status=400)
        try:
            contact = Contact.objects.get(pk=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({'detail': 'Контакт не найден.'}, status=400)

        for item in items:
            if not item.product_info.shop.state:
                return Response({'detail': f'Поставщик {item.product_info.shop.name} не принимает заказы.'}, status=400)
            if item.quantity > item.product_info.quantity:
                return Response({'detail': f'Недостаточно товара: {item.product_info.product.name}'}, status=400)

        order = Order.objects.create(user=request.user, contact=contact, state='new')
        for item in items:
            info = item.product_info
            OrderItem.objects.create(order=order, product_info=info, quantity=item.quantity, price=info.price)
            info.quantity -= item.quantity
            info.save(update_fields=['quantity'])
        CartItem.objects.filter(user=request.user).delete()

        message = f'Заказ #{order.id} принят. Сумма: {order.total()}.'
        send_order_email.delay('Подтверждение заказа', message, request.user.email)
        send_order_email.delay(f'Новый заказ #{order.id}', message, settings.ADMIN_EMAIL)
        return Response(OrderSerializer(order).data, status=201)


class OrderStatusView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return Order.objects.all()

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'detail': 'Требуются права администратора.'}, status=403)
        order = self.get_object()
        state = request.data.get('state')
        if state not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'Некорректный статус.'}, status=400)
        order.state = state
        order.save(update_fields=['state'])
        send_order_email.delay(
            f'Статус заказа #{order.id}',
            f'Статус заказа изменён: {order.get_state_display()}',
            order.user.email,
        )
        return Response(OrderSerializer(order).data)


class PartnerOrderListView(generics.ListAPIView):
    """Заказы, содержащие товары текущего поставщика."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'detail': 'Доступ разрешён только поставщику.'}, status=403)

        shop = getattr(request.user, 'shop', None)
        if shop is None:
            return Response({'detail': 'К аккаунту не привязан магазин.'}, status=400)

        orders = Order.objects.filter(
            ordered_items__product_info__shop=shop
        ).distinct().select_related('user').prefetch_related(
            'ordered_items__product_info__product',
            'ordered_items__product_info__shop',
        ).order_by('-dt')

        result = []
        for order in orders:
            items = order.ordered_items.filter(product_info__shop=shop).select_related(
                'product_info__product'
            )
            result.append({
                'id': order.id,
                'created_at': order.dt,
                'status': order.state,
                'buyer_email': order.user.email,
                'items': [{
                    'product': item.product_info.product.name,
                    'quantity': item.quantity,
                    'price': str(item.price),
                } for item in items],
            })
        return Response(result)
