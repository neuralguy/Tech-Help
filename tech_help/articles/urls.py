from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('create/', views.article_create, name='article_create'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    path('<slug:slug>/edit/', views.article_edit, name='article_edit'),
    path('<slug:slug>/delete/', views.article_delete, name='article_delete'),
    path('<slug:slug>/comment/add', views.add_comment, name='add_comment'),
    path('<slug:slug>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<slug:slug>/comment/edit/', views.edit_comment, name='edit_comment'),
    path('<slug:slug>/rate/', views.rate_article, name='rate_article'),
    path('<slug:slug>/comment/<int:comment_id>/react/', views.handle_reaction, name='comment_react'),
] 