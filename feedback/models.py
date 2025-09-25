from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from product.models import Product
from users.models import CustomUser


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='reviews')
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user} - {self.product}'


class ProductRating(models.Model):
    CHOICES_RATING = [(1, '1'),
                      (2, '2'),
                      (3, '3'),
                      (4, '4'),
                      (5, '5')]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings', verbose_name='Товар')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings', verbose_name='Пользователь')
    rating = models.SmallIntegerField(verbose_name='Рейтинг', choices=CHOICES_RATING,
                                      validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user} - {self.product} - {self.rating}'

    def count_rating(self):
        if self.product:
            return ProductRating.objects.filter(product=self.product).aggregate(models.Avg('rating'))['rating__avg']
        else:
            return 0


class Question(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь',
                             related_name='questions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='questions')
    text = models.TextField(verbose_name='Текст вопроса')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_answered = models.BooleanField(default=False, verbose_name='Ответ получен')

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        if self.is_answered:
            return f'{self.user} - {self.product} - Ответ получен'
        else:
            return f'{self.user} - {self.product} - Ответ не получен'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    text = models.TextField(verbose_name='Ответ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        unique_together = ['user', 'question']

    def __str__(self):
        return f'{self.question} - {self.user}'

    def save(self, *args, **kwargs):
        if not self.question.is_answered:
            self.question.is_answered = True
            self.question.save()
        super().save(*args, **kwargs)


