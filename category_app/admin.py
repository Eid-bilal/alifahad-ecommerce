from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'is_listed', 'created_at')
    list_filter = ('is_listed',)
    search_fields = ('category_name',)

