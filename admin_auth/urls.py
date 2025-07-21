from django.contrib import admin
from django.urls import path
from admin_auth import views


urlpatterns = [
    path('a_login/', views.admin_login, name='admin_login'),
    path('panel/', views.panel, name='panel'),
    path('user_management/',views.user_managment, name='user_management'),
    path('user/<int:user_id>/block-unblock/',views.block_unblock_user,name='block_unblock_user'),
    path('a_logout/',views.admin_logout,name='admin_logout'),
]