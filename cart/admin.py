from django.contrib import admin

from cart.models import Cart  # лучше всегда использовать абсолютные импорты


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    fields = ["user", "product", "quantity"]
    readonly_fields = ["session_key", "created_timestamp"]
    list_select_related = [
        "product"
    ]  # чтобы не было доп запроса в БД для получения строкового представления объекта (хотя мб и не надо)

    class Meta:
        model = Cart
        fields = "__all__"
