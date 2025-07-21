from django.urls import path
from . import views

urlpatterns = [
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/remove/<int:variant_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('move_to_cart/<int:variant_id>/', views.move_to_cart, name='move_to_cart'),
]


