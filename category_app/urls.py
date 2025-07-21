from django.urls import path
from . import views

urlpatterns = [
    path('category_management/', views.category_management, name='category_management'),  #
    path('edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('toggle/<int:category_id>/', views.toggle_category_listing, name='toggle_category_listing'),  #

]