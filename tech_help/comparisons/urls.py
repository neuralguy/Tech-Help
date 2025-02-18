from django.urls import path
from . import views

app_name = 'comparisons'

urlpatterns = [
    path('', views.comparison_list, name='comparison_list'),
    path('create/', views.comparison_create, name='comparison_create'),
    path('<slug:slug>/', views.comparison_detail, name='comparison_detail'),
    path('<slug:comparison_slug>/vote/<slug:device_slug>/', 
         views.vote_for_device, name='vote_for_device'),
] 