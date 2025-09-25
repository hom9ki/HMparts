from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    list_editable = ('first_name', 'last_name', 'is_active')
    ordering = ('-date_joined',)
    search_fields = ('username', 'email', 'first_name', 'last_name')
    sortable_by = ('is_active',)
    search_help_text = 'Поиск по логину, имени или фамилии'
    actions_on_bottom = True
    fields = ('username', 'email', ('first_name', 'last_name'), 'avatar')
    readonly_fields = ('is_superuser', 'date_joined', 'last_login')
    class Meta:
        model = CustomUser

