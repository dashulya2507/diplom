from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import CartItem
from .serializers import CartItemSerializer
from shop.models import ProductInfo


class CartListView(generics.ListAPIView):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('product_info__product', 'product_info__shop')


class CartAddView(generics.CreateAPIView):
    serializer_class = CartItemSerializer

    def create(self, request, *args, **kwargs):
        try:
            product_info_id = int(request.data.get('product_info'))
            quantity = int(request.data.get('quantity', 1))
        except (TypeError, ValueError):
            raise ValidationError({'detail': 'product_info и quantity должны быть числами.'})

        if quantity < 1:
            raise ValidationError({'detail': 'Количество должно быть положительным.'})
        try:
            info = ProductInfo.objects.select_related('shop').get(pk=product_info_id)
        except ProductInfo.DoesNotExist:
            raise ValidationError({'detail': 'Товар не найден.'})
        if not info.shop.state:
            raise ValidationError({'detail': 'Поставщик временно не принимает заказы.'})

        item, created = CartItem.objects.get_or_create(
            user=request.user, product_info=info, defaults={'quantity': quantity}
        )
        if not created:
            new_quantity = item.quantity + quantity
            if new_quantity > info.quantity:
                raise ValidationError({'detail': 'Недостаточно товара на складе.'})
            item.quantity = new_quantity
            item.save(update_fields=['quantity'])
        elif quantity > info.quantity:
            item.delete()
            raise ValidationError({'detail': 'Недостаточно товара на складе.'})
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)


class CartDeleteView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
