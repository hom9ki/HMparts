from django.urls import path
from . import views

app_name = 'garage'

urlpatterns = [
    path('', views.garage_list, name='garage'),
    path('delete/<int:car_id>', views.delete_car, name='delete_car'),
    path('add/', views.add_car, name='add_car'),
]