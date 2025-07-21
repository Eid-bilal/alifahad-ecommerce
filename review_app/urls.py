from django.urls import path
from .views import submit_review, ratings_and_reviews_admin

urlpatterns = [
    # Other URL patterns...
    path('submit-review/', submit_review, name='submit_review'),
    path('custom-ratings-reviews/', ratings_and_reviews_admin, name='custom_ratings_reviews'),
]
