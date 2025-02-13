from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('make_mutation_cohorts/', views.make_mutation_cohorts, name='make_mutation_cohorts'),
    path('make_c_half_graph/', views.make_c_half_graph, name='make_c_half_graph'),
    path('make_mutation_dendrogram/', views.make_mutation_dendrogram, name='make_mutation_dendrogram'),
    path('make_sex_cohorts/', views.make_sex_cohorts, name='make_sex_cohorts'),
    path('make_drug_cohorts/', views.make_drug_cohorts, name='make_drug_cohorts'),
    path('make_age_cohorts/', views.make_age_cohorts, name='make_age_cohorts'),
    path('make_bmi_cohorts/', views.make_bmi_cohorts, name='make_bmi_cohorts'),
    path('make_disease_cohorts/', views.make_disease_cohorts, name='make_disease_cohorts'),
    path('reset_filters/', views.reset_filters, name='reset_filters'),
    path('filter_bmi/', views.filter_bmi, name='filter_bmi'),
    path('filter_disease/', views.filter_disease, name='filter_disease'),
    path('filter_drugs/', views.filter_drugs, name='filter_drugs'),
    path('filter_sex/', views.filter_sex, name='filter_sex'),
    path('filter_age/', views.filter_age, name='filter_age'),
    path('reset_database/', views.reset_database, name='reset_database')
]
