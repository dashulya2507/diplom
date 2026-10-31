from django.db import models

class Shop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(blank=True, null=True)
    state = models.BooleanField(default=True)
    user = models.OneToOneField('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='shop')
    def __str__(self): return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True)
    def __str__(self): return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_infos')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_infos')
    model = models.CharField(max_length=200, blank=True)
    external_id = models.PositiveBigIntegerField()
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_rrc = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['product','shop','external_id'], name='unique_product_info')]
    def __str__(self): return f'{self.product} — {self.shop}'

class Parameter(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name

class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='product_parameters')
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='product_parameters')
    value = models.CharField(max_length=255)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['product_info','parameter'], name='unique_product_parameter')]

class Contact(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='contacts')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    patronymic = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=150)
    house = models.CharField(max_length=20)
    structure = models.CharField(max_length=20, blank=True)
    building = models.CharField(max_length=20, blank=True)
    apartment = models.CharField(max_length=20, blank=True)
    def __str__(self): return f'{self.city}, {self.street}, {self.house}'
