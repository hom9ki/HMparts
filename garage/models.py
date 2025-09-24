from django.db import models

from users.models import CustomUser


class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Марка автомобиля')

    class Meta:
        verbose_name = 'Марка автомобиля'
        verbose_name_plural = 'Марки автомобилей'
        ordering = ['name']

    def __str__(self):
        return self.name


class Model(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Марка автомобиля')
    name = models.CharField(max_length=50, verbose_name='Модель автомобиля')
    image = models.ImageField(upload_to='models/', blank=True, null=True, verbose_name='Изображение модели')

    class Meta:
        verbose_name = 'Модель автомобиля'
        verbose_name_plural = 'Модели автомобилей'

    def __str__(self):
        return f'{self.brand.name} {self.name}'


class Garage(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    models = models.ManyToManyField(Model, through='UserCar', through_fields=('garage', 'car_model'),
                                    verbose_name='Модели автомобилей')

    class Meta:
        verbose_name = 'Гараж'
        verbose_name_plural = 'Гаражи'
    def __str__(self):
        if self.user.first_name:
            return f'{self.user.first_name} {self.user.last_name}'
        else:
            return f'{self.user.username}'

class UserCar(models.Model):
    garage = models.ForeignKey(Garage, on_delete=models.CASCADE, verbose_name='Гараж', related_name='garage')
    car_model = models.ForeignKey(Model, on_delete=models.CASCADE, verbose_name='Модель автомобиля')
    is_main = models.BooleanField(default=False, verbose_name='Основной автомобиль')

    class Meta:
        verbose_name = 'Автомобиль пользователя'
        verbose_name_plural = 'Автомобили пользователя'

    def __str__(self):
        return f'{self.garage.user.username} {self.car_model.name}'