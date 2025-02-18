from django.urls import path
from . import views

app_name = 'devices'

urlpatterns = [
    path('', views.device_list, name='device_list'),
    path('create/', views.device_create, name='device_create'),
    path('<slug:slug>/', views.device_detail, name='device_detail'),
    path('<slug:slug>/edit/', views.device_edit, name='device_edit'),
    path('<slug:slug>/delete/', views.device_delete, name='device_delete'),
    path('specification/create/', views.specification_create, name='specification_create'),
]
