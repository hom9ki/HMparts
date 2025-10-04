from django.urls import path

from . import views

app_name = 'product'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_card, name='product_card'),
    path('supercategory/', views.supercategory, name='supercategory'),
    path('subcategory/<slug:slug>/', views.subcategory, name='subcategory'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('category/subcategory/<slug:slug>/', views.category_detail, name='category_detail'),
    path('category/', views.category, name='category_all'),
    path('sets/', views.set_all, name='set_all'),
    path('set/<slug:slug>/', views.set_detail, name='set_detail'),
    path('search/', views.search_product_set, name='search'),

    path('api/product/<slug:slug>/<str:action>/', views.product_api, name='product_api'),
    # path('api/review/<slug:slug>/', views.add_review, name='add_review'),
]
