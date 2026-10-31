from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from cart.models import CartItem
from orders.models import Order
from shop.models import Category, Product, ProductInfo, Shop
from users.models import ConfirmEmailToken, User


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123', is_active=True)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.user).key}')
        shop = Shop.objects.create(name='Test shop')
        category = Category.objects.create(name='Phones')
        category.shops.add(shop)
        product = Product.objects.create(name='Phone', category=category)
        self.info = ProductInfo.objects.create(
            product=product, shop=shop, external_id=1, quantity=10, price=100, price_rrc=120
        )

    def test_products(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_cart(self):
        response = self.client.post('/api/cart/add/', {'product_info': self.info.id, 'quantity': 2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.client.get('/api/cart/').json()[0]['quantity'], 2)

    def test_order(self):
        self.client.post('/api/cart/add/', {'product_info': self.info.id, 'quantity': 2})
        contact = self.client.post('/api/contacts/', {
            'first_name': 'Иван', 'last_name': 'Иванов', 'phone': '+79990000000',
            'city': 'Москва', 'street': 'Тверская', 'house': '1', 'email': 'test@example.com'
        })
        self.assertEqual(contact.status_code, 201)
        response = self.client.post('/api/orders/create/', {'contact_id': contact.json()['id']})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['total'], '200.00')
        self.assertEqual(Order.objects.count(), 1)
        self.info.refresh_from_db()
        self.assertEqual(self.info.quantity, 8)
        self.assertEqual(CartItem.objects.count(), 0)
        self.assertGreaterEqual(len(mail.outbox), 2)

    def test_registration_and_confirmation(self):
        client = APIClient()
        response = client.post('/api/register/', {
            'first_name': 'Dasha', 'last_name': 'Test', 'email': 'new@example.com', 'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='new@example.com')
        self.assertFalse(user.is_active)
        token = ConfirmEmailToken.objects.get(user=user)
        response = client.post('/api/register/confirm/', {'email': user.email, 'token': token.key})
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_import_command(self):
        call_command('import_products', 'data/shop1.yaml')
        imported_shop = Shop.objects.get(name='Связной')
        self.assertEqual(imported_shop.product_infos.count(), 14)
