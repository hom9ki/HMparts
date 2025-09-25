from django.contrib import admin

from .models import Review, Answer, Question, ProductRating


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    class Meta:
        model = Review
        fields = '__all__'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    class Meta:
        model = Answer
        fields = '__all__'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    class Meta:
        model = Question
        fields = '__all__'


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    class Meta:
        model = ProductRating
        fields = '__all__'
