from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('make_cohorts/', views.make_cohorts, name='make_cohorts'),
    path('make_c_half_graph/', views.make_c_half_graph, name='make_c_half_graph'),
    # path('clear_cohorts/', views.clear_cohorts, name='clear_cohorts'),
    path('dendrogram/', views.make_dendrogram, name='make_dendrogram'),
    path('make_sex_cohorts/', views.make_sex_cohorts, name='make_sex_cohorts'),
    path('make_drug_cohorts/', views.make_drug_cohorts, name='make_drug_cohorts'),
    path('make_age_cohorts/', views.make_age_cohorts, name='make_age_cohorts'),
    path('make_bmi_cohorts/', views.make_bmi_cohorts, name='make_bmi_cohorts'),
    path('make_disease_cohorts/', views.make_disease_cohorts, name='make_disease_cohorts'),
    path('reset_filters/', views.reset_filters, name='reset_filters'),
    path('filter_bmi/', views.filter_bmi, name='filter_bmi'),
    path('filter_age/', views.filter_age, name='filter_age')
    # ,
    # path('make_cohorts2/', views.make_cohorts2, name='make_cohorts2')
]
