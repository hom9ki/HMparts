from django.db.models import Avg
from rest_framework import serializers

from .models import ProductDescription, Set
from feedback.models import Review, Question, Answer


class ProductDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDescription
        fields = '__all__'


class SetSerializer(serializers.ModelSerializer):
    total_price = serializers.CharField(source='get_total_price', read_only=True)

    class Meta:
        model = Set
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'

    def get_avatar(self, obj):
        if obj.user.avatar:
            print(obj.user.avatar.url)
            return obj.user.avatar.url
        return None

    def get_rating(self, obj):
        if obj.product.ratings.all():
            return obj.product.ratings.aggregate(Avg('rating'))['rating__avg']
        else:
            return None


class AnswerSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Answer
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'
