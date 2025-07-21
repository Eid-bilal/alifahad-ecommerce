from django.urls import path
from . import views


urlpatterns = [

    #-----------User Profile----------#
    path('user_profile/', views.user_profile, name='user_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),

    #-----------User Address----------#
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),

    #-----------User Checkout Address----------#
    path('add_checkout_address/', views.add_checkout_address, name='add_checkout_address'),
    path('edit_checkout_address/<int:address_id>/', views.edit_checkout_address, name='edit_checkout_address'),

    #-----------User change Password----------#
    path('change_password/', views.change_password, name='change_password'),

    #-----------Admin User Profile Details----------#
    path('admin_user_profile/', views.admin_user_profile, name='admin_user_profile'),


    # path('order-details/', views.order_details, name='order-details'),
    # path("cancel-order-json/", views.cancel_order_json, name="cancel_order_json"),
]