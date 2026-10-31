from rest_framework import serializers
from .models import CartItem
class CartItemSerializer(serializers.ModelSerializer):
    name=serializers.CharField(source='product_info.product.name', read_only=True)
    shop=serializers.CharField(source='product_info.shop.name', read_only=True)
    price=serializers.DecimalField(source='product_info.price', max_digits=12, decimal_places=2, read_only=True)
    total=serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta: model=CartItem; fields=['id','product_info','name','shop','price','quantity','total']
