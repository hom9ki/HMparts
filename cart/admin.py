from django.contrib import admin

from .models import Cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    fields = ['user', 'product', 'quantity']
    readonly_fields = ['session_key', 'created_timestamp']

    class Meta:
        model = Cart
        fields = '__all__'
