from django.urls import path
from . import views
from board import views as board_views

urlpatterns = [
    path('', views.shelter_list, name='shelter_list'),
    path('<int:pk>/', views.shelter_detail_info, name='shelter_detail'),  # 기본 진입은 기본정보
    path('<int:pk>/info/', views.shelter_detail_info, name='shelter_detail_info'),
    path('<int:pk>/donate/', views.shelter_donate, name='shelter_donate'),
    path('<int:pk>/donate/do/', views.shelter_donate_do, name='shelter_donate_do'),
    path('<int:pk>/donate/process/', views.donate_process, name='donate_process'),
    path('<int:pk>/donations/', views.shelter_donations, name='shelter_donations'),
    path('<int:shelter_pk>/community/', board_views.shelter_community_list, name='shelter_community_list'),
    path('<int:shelter_pk>/community/write/', board_views.shelter_community_post_create, name='shelter_community_post_create'),
    path('<int:shelter_pk>/community/<int:pk>/', board_views.shelter_community_post_detail, name='shelter_community_post_detail'),
]