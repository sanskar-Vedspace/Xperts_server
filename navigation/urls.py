# navigation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/menus/', views.menu_list, name='menu-list'),
]
