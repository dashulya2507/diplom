from django.db import models
from users.models import User
from shop.models import Contact, ProductInfo

class Order(models.Model):
    STATUS_CHOICES = [('new','Новый'),('confirmed','Подтверждён'),('assembled','Собран'),('sent','Отправлен'),('delivered','Доставлен'),('canceled','Отменён')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    def total(self): return sum(i.quantity * i.price for i in self.ordered_items.all())
    def __str__(self): return f'Заказ #{self.pk}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ordered_items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['order','product_info'], name='unique_order_item')]
