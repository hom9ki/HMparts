from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('api/cart/', views.cart_list, name='cart_list_api'),
    path('api/cart/add/<slug:product_slug>/', views.cart_add, name='cart_add'),
    path('api/cart/remove/<slug:product_slug>/', views.cart_remove, name='cart_remove'),
    # path('cart_change/<slug:product_slug>/', views.cart_change, name='cart_change'),
    path('cart_detail/', views.cart_detail, name='cart_detail'),
]
