from django.urls import path
from . import views


urlpatterns = [
    path('coupon_list/', views.coupon_list, name='coupon_list'),
    path('coupon_add/', views.coupon_add, name='coupon_add'),
    path('coupon_edit/<int:coupon_id>/', views.coupon_edit, name='coupon_edit'),
    path('coupon_delete/<int:coupon_id>/', views.coupon_delete, name='coupon_delete'),
]