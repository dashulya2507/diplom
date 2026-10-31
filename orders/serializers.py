from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product_info.product.name', read_only=True)
    shop = serializers.CharField(source='product_info.shop.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'name', 'shop', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='ordered_items', many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'dt', 'state', 'contact', 'total', 'items']
        read_only_fields = ['id', 'dt', 'state', 'total', 'items']

    def get_total(self, obj):
        return obj.total()
