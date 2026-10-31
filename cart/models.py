from django.db import models
from users.models import User
from shop.models import ProductInfo

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','product_info'], name='unique_cart_item')]
    @property
    def total(self): return self.product_info.price * self.quantity
