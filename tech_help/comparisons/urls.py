from django.urls import path
from . import views

app_name = 'comparisons'

urlpatterns = [
    path('devices/', views.device_list, name='device_list'),
    path('device/<slug:slug>/', views.device_detail, name='device_detail'),
    path('create/', views.comparison_create, name='comparison_create'),
    path('comparison/<slug:slug>/', views.comparison_detail, name='comparison_detail'),
    path('comparison/<slug:comparison_slug>/vote/<slug:device_slug>/', 
         views.vote_for_device, name='vote_for_device'),
    path('api/device-specs/', views.get_device_specs, name='get_device_specs'),
    path('device/create/', views.device_create, name='device_create'),
    path('device/<slug:slug>/edit/', views.device_edit, name='device_edit'),
    path('specification/create/', views.specification_create, name='specification_create'),
    path('comparisons/', views.comparison_list, name='comparison_list'),
    path('comparison/create/', views.comparison_create, name='comparison_create'),
] 