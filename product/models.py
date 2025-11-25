from django.db import models
from django.utils import timezone
from .utilities import get_image_filename_category, get_image_filename_product, get_image_filename_set
from garage.models import Model
from .mixins import CatalogMixin


class CategoryManager(models.Manager):
    """Универсальный диспетчер для прокси-модели который позволит задать поведение для Category."""

    def supercategories(self):
        supercategories = self.filter(is_supercategory=True)
        return supercategories

    def subcategories(self):
        return self.filter(is_supercategory=False)

    def supercategories_with_subcategories(self):
        return self.supercategories().prefetch_related('subcategories')

    def get_queryset(self):
        return super().get_queryset().select_related('super_category')


class Category(models.Model):
    """Модель категории"""
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')
    image = models.ImageField(upload_to=get_image_filename_category, blank=True, verbose_name='Изображение')
    is_supercategory = models.BooleanField(default=False, verbose_name='Суперкатегория')
    super_category = models.ForeignKey('SuperCategory', on_delete=models.PROTECT,
                                       null=True, blank=True, limit_choices_to={'is_supercategory': True},
                                       verbose_name='Родительская категория', related_name='subcategories')

    objects = CategoryManager()

    def __str__(self):
        return self.name


class SuperCategory(Category):
    """Прокси-модель для суперкатегорий"""

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.super_category = None
        self.is_supercategory = True
        super().save(*args, **kwargs)

    class Meta:
        proxy = True
        ordering = ['name', 'slug']
        verbose_name = 'Суперкатегория'
        verbose_name_plural = 'Суперкатегории'


class SubCategory(Category):
    """Прокси-модель подкатегории"""

    def __str__(self):
        if self.super_category:
            return f'{self.super_category.name} - {self.name}'
        else:
            return f'{self.name}'

    class Meta:
        proxy = True
        ordering = ['super_category__name', 'name', 'slug']
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'


class Product(models.Model, CatalogMixin):
    """Модель товара"""
    category = models.ForeignKey(SubCategory, on_delete=models.PROTECT, verbose_name='Категория',
                                 related_name='products')
    title = models.CharField(max_length=200, verbose_name='Название товара')
    slug = models.SlugField(max_length=250, unique=True, verbose_name='URL')
    content = models.TextField(verbose_name='Описание товара')
    price = models.FloatField(default=0, verbose_name='Цена')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    image = models.ImageField(blank=True, upload_to=get_image_filename_product, verbose_name='Изображение')
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name='Автор',
                               related_name='products')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def delete(self, *args, **kwargs):
        """Удаление товара вместе с его изображениями с помощью django-cleanup"""
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']

    def __str__(self):
        if len(self.title) > 50:
            return self.title[:50] + '...'
        else:
            return self.title

    @property
    def sku(self):
        return f'AP{str(self.id):>05}'


class AdditionalImage(models.Model):
    """Модель дополнительного изображения товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    image = models.ImageField(upload_to=get_image_filename_product, verbose_name='Дополнительное изображение')

    class Meta:
        verbose_name = 'Дополнительное изображение'
        verbose_name_plural = 'Дополнительные изображения'


class ProductApplicability(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, verbose_name='Товар',
                                   related_name='applicability')
    model = models.ManyToManyField(Model, verbose_name='Модель', related_name='applicability_products')

    class Meta:
        verbose_name = 'Применяемость'
        verbose_name_plural = 'Применяемость'

    def __str__(self):
        return f'Применяемость для {self.product.title}'


class HitBase(models.Model):
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')

    class Meta:
        abstract = True


class HitProduct(HitBase):
    """Модель хит товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Хит товар', related_name='hits')

    class Meta:
        verbose_name = 'Хит товара'
        verbose_name_plural = 'Хиты товаров'
        ordering = ['-created_at']


class HitSet(HitBase):
    """Модель хит комплекта"""
    set_object = models.ForeignKey('Set', on_delete=models.CASCADE, verbose_name='Хит комплект', related_name='hits')

    class Meta:
        verbose_name = 'Хит комплекта'
        verbose_name_plural = 'Хиты комплектов'
        ordering = ['-created_at']


class Set(models.Model, CatalogMixin):
    """Модель комплекта товаров"""
    products = models.ManyToManyField(Product, through='SetProduct', verbose_name='Товары', related_name='sets')
    name = models.CharField(max_length=100, verbose_name='Название сета')
    slug = models.SlugField(max_length=150, unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание сета')
    image = models.ImageField(upload_to=get_image_filename_set, verbose_name='Изображение сета')
    total_price = models.FloatField(default=0, verbose_name='Общая цена')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    discount = models.FloatField(default=0, verbose_name='Скидка в процентах')

    class Meta:
        verbose_name = 'Комплект'
        verbose_name_plural = 'Комплекты'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_total_price(self):
        """Получение общей цены комплекта со скидкой"""
        from django.db.models import Sum, F
        price = Set.objects.filter(pk=self.pk).annotate(
            individual_price=Sum(
                F('set_products__product__price') * F('set_products__quantity'))).first().individual_price or 0

        return round(price * (1 - self.discount / 100), 0)

    def get_savings(self):
        """Получение скидки на комплект"""
        return self.total_price - self.get_total_price()

    def get_quantity(self):
        """Получение количества комплектов"""
        from django.db.models import Min, F, ExpressionWrapper, IntegerField
        quantity = Set.objects.filter(pk=self.pk).annotate(
            individual_quantity=Min(
                ExpressionWrapper(F('set_products__product__quantity'), output_field=IntegerField()))).first() or 0

        return quantity.individual_quantity


class SetProduct(models.Model):
    """Модель товара в комплекте"""
    set = models.ForeignKey(Set, on_delete=models.CASCADE, verbose_name='Комплект', related_name='set_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')

    class Meta:
        verbose_name = 'Товар в комплекте'
        verbose_name_plural = 'Товары в комплекте'

    def __str__(self):
        return f'{self.set.name} - {self.product.title}'


class ProductDescription(models.Model):
    """Модель описания товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='descriptions')
    description_type = models.CharField(max_length=200, verbose_name='Тип описания')
    content = models.TextField(verbose_name='Описание')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')

    class Meta:
        verbose_name = 'Описание товара'
        verbose_name_plural = 'Описания товаров'

    def __str__(self):
        return f'{self.description_type} - {self.content}'


class DynamicDescriptionField(models.Model):
    """Модель динамического поля"""
    FIELDS_CHOICES = [('text', 'Текст'), ('number', 'Число'),
                      ('boolean', 'Да/Нет'), ('select', 'Выбор из списка')]

    name = models.CharField(max_length=100, verbose_name='Название поля')
    field_type = models.CharField(max_length=20, choices=FIELDS_CHOICES, verbose_name='Тип поля')
    options = models.JSONField(blank=True, null=True, verbose_name='Опции')

    class Meta:
        verbose_name = 'Динамическое поле'
        verbose_name_plural = 'Динамические поля'

    def __str__(self):
        return f'{self.name}'


class ProductDynamicDescription(models.Model):
    """Модель динамического описания товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар',
                                related_name='dynamic_descriptions')
    field = models.ForeignKey(DynamicDescriptionField, on_delete=models.CASCADE, verbose_name='Поле',
                              related_name='dynamic_descriptions')
    value = models.TextField(blank=True, null=True, verbose_name='Значение')

    class Meta:
        verbose_name = 'Динамическое описание товара'
        verbose_name_plural = 'Динамические описания товаров'

    def __str__(self):
        return f'{self.product.title} - {self.field.name}'
