from django.urls import path
from product_app import views


urlpatterns = [
    path('product_management/',views.product_list, name='product_management'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('toggle-product-listing/<int:product_id>/', views.toggle_product_listing, name='toggle_product_listing'),    
    path('product_view/',views.user_products, name='user_products'),
    # path('product_details/<int:product_id>/',views.product_details, name='product_details'),

    
    path('variant_list/<int:product_id>/', views.variant_list, name='variant_list'),
    path('add_variant/<int:product_id>/', views.add_variant, name='add_variant'),
    path('update_variant/<int:variant_id>/', views.update_variant, name='update_variant'),


  
    path('product/<int:product_id>/', views.product_details, name='product_details'),
    


    
    
    
    
]