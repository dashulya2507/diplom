from rest_framework import serializers
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact

class ShopSerializer(serializers.ModelSerializer):
    class Meta: model=Shop; fields='__all__'
class CategorySerializer(serializers.ModelSerializer):
    class Meta: model=Category; fields=['id','name']
class ProductParameterSerializer(serializers.ModelSerializer):
    name=serializers.CharField(source='parameter.name')
    class Meta: model=ProductParameter; fields=['name','value']
class ProductInfoSerializer(serializers.ModelSerializer):
    shop=serializers.CharField(source='shop.name', read_only=True)
    product=serializers.IntegerField(source='product.id', read_only=True)
    parameters=ProductParameterSerializer(source='product_parameters', many=True, read_only=True)
    class Meta: model=ProductInfo; fields=['id','product','shop','model','quantity','price','price_rrc','parameters']
class ProductSerializer(serializers.ModelSerializer):
    category=serializers.CharField(source='category.name', read_only=True)
    offers=ProductInfoSerializer(source='product_infos', many=True, read_only=True)
    class Meta: model=Product; fields=['id','name','description','category','offers']
class ContactSerializer(serializers.ModelSerializer):
    class Meta: model=Contact; exclude=['user']
