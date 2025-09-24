from django.contrib import admin
from .models import Brand, Model, Garage, UserCar


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    fields = ['name']
    search_fields = ['name']


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    fields = [('brand', 'name'), 'image', ]
    search_fields = ['name', 'brand__name']

class ModelInline(admin.TabularInline):
    model = Model
    extra = 1

class UserCarInline(admin.TabularInline):
    model = UserCar

@admin.register(Garage)
class GarageAdmin(admin.ModelAdmin):
    fields = ['user']
    inlines = [UserCarInline,]

@admin.register(UserCar)
class UserCarAdmin(admin.ModelAdmin):
    fields = ['garage', 'car_model', 'is_main']
    readonly_fields = ['car_model', 'garage', 'is_main', ]




