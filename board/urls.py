from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_list, name='community_list'),
    path('write/', views.community_post_create, name='community_post_create'),
    path('<int:pk>/', views.community_post_detail, name='community_post_detail'),
]
