from django.db import models
from users.models import CustomUser
from product.models import Product


class CartQuerySet(models.QuerySet):
    def total_price(self):
        return sum(cart.product_price() for cart in self)

    def total_quantity(self):
        return sum(cart.quantity for cart in self)


class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Пользователь',
                             related_name='user_cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, verbose_name='Товар',
                                related_name='product_cart')
    quantity = models.SmallIntegerField(default=0, verbose_name='Количество')
    session_key = models.CharField(max_length=255, blank=True, null=True)
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    objects = CartQuerySet().as_manager()

    def product_price(self):
        return round(self.product.price * self.quantity, 2)

    def __str__(self):
        return f'{self.user} - {self.product} - {self.quantity}'
