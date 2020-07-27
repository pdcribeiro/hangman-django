from django.urls import path

from . import views

urlpatterns = [
    path('', views.lobby, name='lobby'),
    path('game/', views.room, name='room'),
    path('leave/', views.leave, name='leave'),
]
