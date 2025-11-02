from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from .models import ProductDescription, Set, Product
from feedback.models import ProductReview, ProductQuestion, Answer, SetReview, SetQuestion


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

    class Meta:
        model = ProductReview
        fields = '__all__'

    def get_avatar(self, obj):
        if obj.user.avatar:
            print(obj.user.avatar.url)
            return obj.user.avatar.url
        else:
            return None


class SetReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = SetReview
        fields = '__all__'

    def get_avatar(self, obj):
        if obj.user.avatar:
            print(obj.user.avatar.url)
            return obj.user.avatar.url
        return None


class AnswerSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Answer
        fields = '__all__'


class ProductQuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ProductQuestion
        fields = '__all__'

    def get_answers(self, obj):
        content_type = ContentType.objects.get_for_model(ProductQuestion)
        answers = Answer.objects.filter(content_type=content_type, object_id=obj.id).select_related('user')
        return AnswerSerializer(answers, many=True).data


class SetQuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = SetQuestion
        fields = '__all__'

    def get_answers(self, obj):
        content_type = ContentType.objects.get_for_model(ProductQuestion)
        answers = Answer.objects.filter(content_type=content_type, object_id=obj.id).select_related('user')
        return AnswerSerializer(answers, many=True).data


class SetDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Set
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
