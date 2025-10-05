from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models import Q

from product.models import Product, Set
from users.models import CustomUser


class ReviewManager(models.Manager):
    def get_avg_rating(self, obj):
        rating = self.filter(Q(product=obj) | Q(set=obj), rating__isnul=False, rating__gt=0).aggregate(
            avr_rating=models.Avg('rating'))
        return rating['avr_rating'] or 0


class BaseReview(models.Model):
    CHOICES_RATING = [(1, '1'),
                      (2, '2'),
                      (3, '3'),
                      (4, '4'),
                      (5, '5')]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.SmallIntegerField(verbose_name='Рейтинг', default=0, choices=CHOICES_RATING)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    objects = ReviewManager()

    class Meta:
        abstract = True

    def get_user_name(self):
        if self.user.first_name and self.user.last_name:
            return f'{self.user.first_name} {self.user.last_name}'
        else:
            return self.user.username


class ProductReview(BaseReview):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='product_reviews')

    class Meta:
        verbose_name = 'Отзыв о товаре'
        verbose_name_plural = 'Отзывы о товарах'
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.product}'


class SetReview(BaseReview):
    set = models.ForeignKey(Set, on_delete=models.CASCADE, verbose_name='Набор', related_name='set_reviews')

    class Meta:
        verbose_name = 'Отзыв о комплекте'
        verbose_name_plural = 'Отзывы о комплектах'
        unique_together = ['user', 'set']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.set}'


class BaseQuestion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст вопроса')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_answered = models.BooleanField(default=False, verbose_name='Ответ получен')

    class Meta:
        abstract = True
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']


class ProductQuestion(BaseQuestion):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар',
                                related_name='product_questions')

    class Meta:
        verbose_name = 'Вопрос о товаре'
        verbose_name_plural = 'Вопросы о товарах'

    def __str__(self):
        if self.is_answered:
            return f'{self.product} - {self.user} - Ответ получен'
        else:
            return f'{self.product} - {self.user} - Ответ не получен'


class SetQuestion(BaseQuestion):
    set = models.ForeignKey(Set, on_delete=models.CASCADE, verbose_name='Набор', related_name='set_questions')

    class Meta:
        verbose_name = 'Вопрос о комплекте'
        verbose_name_plural = 'Вопросы о комплектах'

    def __str__(self):
        if self.is_answered:
            return f'{self.set} - {self.user} - Ответ получен'
        else:
            return f'{self.set} - {self.user} - Ответ не получен'


class GeneralQuestion(BaseQuestion):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь',
                             related_name='general_questions')

    class Meta:
        verbose_name = 'Общий вопрос'
        verbose_name_plural = 'Общие вопросы'

    def __str__(self):
        if self.is_answered:
            return f'{self.user} - Ответ получен'
        else:
            return f'{self.user} - Ответ не получен'


class Answer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Ответ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    question = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        constraints = [
            models.UniqueConstraint(fields=['content_type', 'object_id', 'user'], name='unique_answer_per_question')
        ]

    def __str__(self):
        return f'{self.question} - {self.user}'

    def save(self, *args, **kwargs):
        if self.question and not self.content_type_id:
            self.content_type = ContentType.objects.get_for_model(self.question)
            self.object_id = self.question.id
        super().save(*args, **kwargs)

        if self.question and not self.question.is_answered:
            self.question.is_answered = True
            self.question.save()
