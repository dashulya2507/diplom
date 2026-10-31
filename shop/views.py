from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Contact, Product, ProductInfo, Shop
from .serializers import CategorySerializer, ContactSerializer, ProductInfoSerializer, ProductSerializer, ShopSerializer
from .services import import_shop_data


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.select_related('category').prefetch_related(
        'product_infos__shop', 'product_infos__product_parameters__parameter'
    ).all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'product_infos__model']

    def get_queryset(self):
        qs = super().get_queryset()
        shop = self.request.query_params.get('shop') or self.request.query_params.get('shop_id')
        category = self.request.query_params.get('category') or self.request.query_params.get('category_id')
        if shop:
            qs = qs.filter(product_infos__shop_id=shop).distinct()
        if category:
            qs = qs.filter(category_id=category)
        return qs


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category').prefetch_related(
        'product_infos__shop', 'product_infos__product_parameters__parameter'
    )
    serializer_class = ProductSerializer


class ProductInfoView(generics.RetrieveAPIView):
    queryset = ProductInfo.objects.select_related('product', 'shop').prefetch_related('product_parameters__parameter')
    serializer_class = ProductInfoSerializer


class ShopListView(generics.ListAPIView):
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]


class ContactListCreateView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContactDeleteView(generics.DestroyAPIView):
    serializer_class = ContactSerializer

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)


class PartnerUpdateView(APIView):
    def post(self, request):
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для поставщика.'}, status=status.HTTP_403_FORBIDDEN)
        url = request.data.get('url')
        if not url:
            return Response({'Status': False, 'Error': 'Не указан url.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            URLValidator()(url)
        except ValidationError:
            return Response({'Status': False, 'Error': 'Некорректный URL.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            shop = import_shop_data(url)
        except Exception as exc:
            return Response({'Status': False, 'Error': f'Не удалось импортировать прайс: {exc}'}, status=status.HTTP_400_BAD_REQUEST)
        if shop.user_id and shop.user_id != request.user.id:
            return Response({'Status': False, 'Error': 'Этот магазин уже привязан к другому аккаунту.'}, status=status.HTTP_403_FORBIDDEN)
        shop.user = request.user
        shop.url = url
        shop.save(update_fields=['user', 'url'])
        return Response({'Status': True, 'shop': shop.name})


class PartnerStateView(APIView):
    def post(self, request):
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для поставщика.'}, status=403)
        shop = getattr(request.user, 'shop', None)
        if shop is None:
            return Response({'Status': False, 'Error': 'Поставщик не привязан к магазину.'}, status=400)
        from rest_framework import serializers
        if 'state' not in request.data:
            return Response({'Status': False, 'Error': 'Укажите state: true или false.'}, status=400)
        try:
            new_state = serializers.BooleanField().to_internal_value(request.data['state'])
        except serializers.ValidationError:
            return Response({'Status': False, 'Error': 'state должен быть true или false.'}, status=400)
        shop.state = new_state
        shop.save(update_fields=['state'])
        return Response({'Status': True, 'state': shop.state})
