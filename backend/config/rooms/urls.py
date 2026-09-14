from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('create/', views.create_room_view, name='create_room'),
    path('room/<str:code>/', views.room_detail_view, name='room_detail'),
]