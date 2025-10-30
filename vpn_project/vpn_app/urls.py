# vpn_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Главная страница и ошибки
    path('', views.index_view, name='index'),
    path('error/', views.error_page, name='error_page'),

    # Аутентификация
    path('auth/', views.login_register_view, name='login_register_page'),
    path('auth/login/', views.login_user, name='login_user_url'),
    path('auth/register/', views.register_user, name='register_user_url'),
    path('auth/logout/', views.logout_user, name='logout_user_url'),

    # Панель управления
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Управление группами
    path('group/create/', views.create_group, name='create_group_url'),
    path('group/leave/<int:id>/', views.leave_group, name='leave_group_url'),
    path('group/delete/<int:id>/', views.delete_group, name='delete_group_url'),
    path('group/remove_member/<int:member_id>/', views.remove_member, name='remove_member_url'),

    # Присоединение к группе и приглашения
    path('group/join/menu/', views.join_group_menu, name='join_menu_url'),
    path('group/invite/generate/', views.generate_invite_link, name='generate_invite_url'),
    path('group/invite/', views.group_invite_modal, name='group_invite_modal'),
    path('group/join/<str:id>/', views.join_group_view, name='join_group_url'),

    # Peer List
    path('group/peers/generate/', views.share_peerlist, name='generate_peers_url'),
    path('group/peers/<str:link>/', views.get_peers, name='get_peers_url'),
]