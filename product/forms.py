from django import forms

from .models import SubCategory, Category


class SubCategoryForm(forms.ModelForm):
    """Форма для отображения категорий в админке"""
    super_category = forms.ModelChoiceField(
        queryset=Category.objects.supercategories(),
        empty_label='---',
        label='Надкатегория', required=False
    )
    class Meta:
        model = SubCategory
        fields = ('super_category', 'name', 'slug')