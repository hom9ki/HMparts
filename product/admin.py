from django.contrib import admin
from .models import SubCategory, SuperCategory, Product, AdditionalImage, HitProduct, SetProduct, Set, HitSet, HitBase
from .models import ProductDescription, DynamicDescriptionField, ProductDynamicDescription, ProductApplicability
from .forms import SubCategoryForm, ProductApplicabilityFormAdmin


class SubCategoryInline(admin.TabularInline):
    """Встроенный редактор для подкатегорий"""
    model = SubCategory


@admin.register(SuperCategory)
class SuperCategoryAdmin(admin.ModelAdmin):
    exclude = ('super_category',)
    inline = (SubCategoryInline,)
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        """Выбор только суперкатегорий"""
        return super().get_queryset(request).filter(is_supercategory=True)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    form = SubCategoryForm
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        """Выбор только подкатегорий"""
        return super().get_queryset(request).filter(is_supercategory=False)


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage


@admin.register(ProductDescription)
class ProductDescriptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'description_type')

    class Meta:
        model = ProductDescription


@admin.register(DynamicDescriptionField)
class DynamicDescriptionFieldAdmin(admin.ModelAdmin):
    list_display = ('name',)

    class Meta:
        model = DynamicDescriptionField


@admin.register(ProductDynamicDescription)
class ProductDynamicDescriptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'field', 'value')
    search_fields = ('product__title',)

    class Meta:
        model = ProductDynamicDescription


class ProductDescriptionInline(admin.TabularInline):
    model = ProductDescription
    extra = 1


class ProductDynamicDescriptionInline(admin.TabularInline):
    model = ProductDynamicDescription
    extra = 1


class ProductApplicabilityInline(admin.TabularInline):
    model = ProductApplicability
    form = ProductApplicabilityFormAdmin
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'content', 'quantity', 'price', 'author', 'created_at')
    search_fields = ('title', 'category__name', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    fields = (('category', 'title', 'slug'), 'content', 'price', 'image', 'quantity', 'created_at')
    list_filter = ('category',)
    exclude = ('author',)
    inlines = (AdditionalImageInline, ProductDescriptionInline, ProductDynamicDescriptionInline,
               ProductApplicabilityInline)
    readonly_fields = ['created_at']

    def save_model(self, request, obj, form, change):
        """При сохранении модели автор будет создан автоматически, и равен текущему пользователю"""
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Суперпользователю и стафу доступны все товары, а обычным пользователям только свои"""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        return qs.filter(author=request.user)


@admin.register(HitProduct)
class HitProductAdmin(admin.ModelAdmin):
    fields = ('product', 'created_at')
    list_display = ('product', 'created_at')
    search_fields = ('product',)
    readonly_fields = ['created_at']

    class Meta:
        model = HitProduct


@admin.register(HitSet)
class HitSetAdmin(admin.ModelAdmin):
    fields = ('set_object', 'created_at')
    list_display = ('set_object', 'created_at')
    search_fields = ('set_object',)
    readonly_fields = ['created_at']

    class Meta:
        model = HitSet


class SetProductInline(admin.TabularInline):
    model = SetProduct
    extra = 1


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    inlines = (SetProductInline,)
    prepopulated_fields = {'slug': ('name',)}
    fields = ['name', 'slug', 'description', 'image', 'total_price', 'discount']


@admin.register(ProductApplicability)
class ProductApplicabilityAdmin(admin.ModelAdmin):
    form = ProductApplicabilityFormAdmin
    list_filter = ('product',)
