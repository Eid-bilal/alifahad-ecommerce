from django.urls import path
from . import views

app_name = 'user'  # Namespace for the app

urlpatterns = [
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_show, name='cart_show'),  # Show cart
    path('cart/update-item/', views.update_cart_item_quantity, name='update_cart_item_quantity'),  # Update cart item quantity
    path('cart/remove-item/', views.remove_cart_item, name='remove_cart_item'),  # Remove item from cart
]
