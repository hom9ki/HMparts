from django.urls import path

from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback, name='index'),
    path('answer/', views.answer, name='answer'),

    path('api/review/<slug:slug>/', views.add_review, name='api_review'),
]
