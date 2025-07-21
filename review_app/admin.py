from django.contrib import admin
from .models import Rating, Review

# Register your models here.

admin.site.register(Rating)
admin.site.register(Review)