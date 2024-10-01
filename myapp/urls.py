from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('make_cohorts/', views.make_cohorts, name='make_cohorts')
]
