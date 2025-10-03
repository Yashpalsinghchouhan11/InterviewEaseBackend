from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('signup/', views.signUp, name='singup'),
    path('login/', views.login, name='login'),
    path('verify_token/<str:token>',views.verify_token,name='verify_token')
]