from django.contrib import admin
from .models import VariantSize

@admin.register(VariantSize)
class VariantSizeAdmin(admin.ModelAdmin):
    list_display = ('size_name', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('size_name',)
