from rest_framework import serializers

from .models import UserCar, Brand, Model

class UserCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCar
        fields = ('car_model', 'is_main')

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name')

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ('name',)

