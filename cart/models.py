from django.db import models
from django.db.models.functions import Round

from product.models import Product
from users.models import CustomUser


class CartItemsQuerySet(models.QuerySet):
    def total_price(self):
        return sum(cart_item.price for cart_item in self.annotate_prices())

    def total_quantity(self):
        return sum(cart_item.quantity for cart_item in self)

    def annotate_prices(self):
        # оптимальнее считать цены для всего набора сразу, а не по одномму
        return self.annotate(
            price=Round(models.F("product__price") * models.F("quantity"), 2)
        )


class CartItemsManager(models.Manager):
    def get_queryset(self):
        return CartItemsQuerySet(self.model, using=self._db)


# CartItem я бы назвал, у тебя больше на такую логику похоже
class Cart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Пользователь",
        related_name="user_cart",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        default=None,
        verbose_name="Товар",
        related_name="product_cart",
    )
    quantity = models.SmallIntegerField(default=0, verbose_name="Количество")
    session_key = models.CharField(max_length=255, blank=True, null=True)
    created_timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Время создания"
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    objects = CartItemsManager()

    def __str__(self):
        # Мы точно не хотим тянуть вызов метода __str__ из модели Продукт
        return f"{self.user}: {self.product.slug} - {self.quantity} шт."
