from django.urls import path
from . import views

app_name = 'garage'

urlpatterns = [
    path('', views.garage_list, name='garage'),
    path('delete/<int:car_id>/', views.delete_car, name='delete_car'),
    path('add/', views.add_car, name='add_car'),
    path('api/detail-cars/<int:pk>/', views.api_user_garage_detail, name='api_car_detail'),
    path('api/brands/', views.api_brand_list, name='api_brand_list'),
    path('api/models/', views.api_model_list, name='api_model_list'),
    path('api/add-cars/', views.api_user_car, name='api_add_car'),
]