from django.contrib import admin

from .models import ProductReview, SetReview, Answer, ProductQuestion, SetQuestion, GeneralQuestion
from django.contrib.contenttypes.admin import GenericStackedInline


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    class Meta:
        model = ProductReview
        fields = '__all__'
        readonly_fields = ['created_at', ]


@admin.register(SetReview)
class SetReviewAdmin(admin.ModelAdmin):
    class Meta:
        model = SetReview
        fields = '__all__'
        readonly_fields = ['created_at', ]


class AnswerInline(GenericStackedInline):
    model = Answer
    fields = ['user', 'text', 'created_at']
    extra = 1
    readonly_fields = ['created_at', ]


@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)

    class Meta:
        model = ProductQuestion
        fields = '__all__'
        readonly_fields = ['created_at', ]


@admin.register(SetQuestion)
class SetQuestionAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)

    class Meta:
        model = SetQuestion
        fields = '__all__'
        readonly_fields = ['created_at', ]


@admin.register(GeneralQuestion)
class GeneralQuestionAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)

    class Meta:
        model = GeneralQuestion
        fields = '__all__'
        readonly_fields = ['created_at', ]
